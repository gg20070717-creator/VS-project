$ErrorActionPreference = 'Stop'

$root = 'd:\VS project\cultural_technology\123\ppt_xml_extracted'
$slidesDir = Join-Path $root 'ppt\slides'
$relsDir = Join-Path $slidesDir '_rels'
$mediaBase = 'ppt_xml_extracted/ppt/media'

function Get-ColorFromFill($fillNode, $nsm) {
  if (-not $fillNode) { return $null }
  $c = $fillNode.SelectSingleNode('./a:srgbClr', $nsm)
  if (-not $c) { return $null }

  $hex = $c.GetAttribute('val')
  $aNode = $c.SelectSingleNode('./a:alpha', $nsm)
  $alpha = 1.0
  if ($aNode) { $alpha = [double]$aNode.GetAttribute('val') / 100000.0 }

  return @{ hex = $hex; alpha = [Math]::Round($alpha, 4) }
}

function Get-Transform($spPr, $nsm) {
  $xfrm = $spPr.SelectSingleNode('./a:xfrm', $nsm)
  if (-not $xfrm) { return @{ x = 0; y = 0; w = 0; h = 0; rot = 0 } }

  $off = $xfrm.SelectSingleNode('./a:off', $nsm)
  $ext = $xfrm.SelectSingleNode('./a:ext', $nsm)
  $rot = 0
  if ($xfrm.Attributes['rot']) { $rot = [double]$xfrm.Attributes['rot'].Value / 60000.0 }

  return @{
    x = [int64]$off.GetAttribute('x')
    y = [int64]$off.GetAttribute('y')
    w = [int64]$ext.GetAttribute('cx')
    h = [int64]$ext.GetAttribute('cy')
    rot = [Math]::Round($rot, 4)
  }
}

$slides = @()
$slideFiles = Get-ChildItem $slidesDir -Filter 'slide*.xml' | Sort-Object { [int]([regex]::Match($_.BaseName, '\d+').Value) }

foreach ($sf in $slideFiles) {
  [xml]$xml = Get-Content -Raw $sf.FullName

  $nsm = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
  $nsm.AddNamespace('p', 'http://schemas.openxmlformats.org/presentationml/2006/main')
  $nsm.AddNamespace('a', 'http://schemas.openxmlformats.org/drawingml/2006/main')
  $nsm.AddNamespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

  $relsPath = Join-Path $relsDir ($sf.Name + '.rels')
  $relMap = @{}
  if (Test-Path $relsPath) {
    [xml]$relsXml = Get-Content -Raw $relsPath
    foreach ($r in $relsXml.Relationships.Relationship) {
      $relMap[$r.Id] = $r.Target
    }
  }

  $bgNode = $xml.SelectSingleNode('//p:cSld/p:bg/p:bgPr/a:solidFill', $nsm)
  $bg = Get-ColorFromFill $bgNode $nsm
  $elements = @()

  $spTree = $xml.SelectSingleNode('//p:cSld/p:spTree', $nsm)
  foreach ($node in $spTree.ChildNodes) {
    if ($node.NamespaceURI -ne 'http://schemas.openxmlformats.org/presentationml/2006/main') { continue }
    if ($node.LocalName -eq 'sp') {
      $sp = $node
      $spPr = $sp.SelectSingleNode('./p:spPr', $nsm)
      if (-not $spPr) { continue }

      $x = Get-Transform $spPr $nsm
      $geom = $spPr.SelectSingleNode('./a:prstGeom', $nsm)
      $prst = 'rect'
      if ($geom -and $geom.Attributes['prst']) { $prst = $geom.Attributes['prst'].Value }

      $fill = Get-ColorFromFill ($spPr.SelectSingleNode('./a:solidFill', $nsm)) $nsm
      $noFill = [bool]($spPr.SelectSingleNode('./a:noFill', $nsm))

      $paragraphs = @()
      $pNodes = $sp.SelectNodes('./p:txBody/a:p', $nsm)
      foreach ($p in $pNodes) {
        $align = 'l'
        $pPr = $p.SelectSingleNode('./a:pPr', $nsm)
        if ($pPr -and $pPr.Attributes['algn']) { $align = $pPr.Attributes['algn'].Value }

        $runs = @()
        $rNodes = $p.SelectNodes('./a:r', $nsm)
        foreach ($r in $rNodes) {
          $rPr = $r.SelectSingleNode('./a:rPr', $nsm)
          $t = $r.SelectSingleNode('./a:t', $nsm)
          if (-not $t) { continue }

          $font = 'Noto Sans SC'
          $sz = 1600
          $b = $false
          $i = $false
          $u = 'none'
          $spc = 0

          if ($rPr) {
            if ($rPr.Attributes['sz']) { $sz = [int]$rPr.Attributes['sz'].Value }
            if ($rPr.Attributes['b']) { $b = ($rPr.Attributes['b'].Value -eq 'true') }
            if ($rPr.Attributes['i']) { $i = ($rPr.Attributes['i'].Value -eq 'true') }
            if ($rPr.Attributes['u']) { $u = $rPr.Attributes['u'].Value }
            if ($rPr.Attributes['spc']) { $spc = [int]$rPr.Attributes['spc'].Value }

            $latin = $rPr.SelectSingleNode('./a:latin', $nsm)
            $ea = $rPr.SelectSingleNode('./a:ea', $nsm)
            if ($ea -and $ea.Attributes['typeface']) {
              $font = $ea.Attributes['typeface'].Value
            }
            elseif ($latin -and $latin.Attributes['typeface']) {
              $font = $latin.Attributes['typeface'].Value
            }
          }

          $txtFill = if ($rPr) { Get-ColorFromFill ($rPr.SelectSingleNode('./a:solidFill', $nsm)) $nsm } else { $null }
          $runs += @{
            text = $t.InnerText
            font = $font
            sz = $sz
            b = $b
            i = $i
            u = $u
            spc = $spc
            color = $txtFill
          }
        }

        $paragraphs += @{ align = $align; runs = $runs }
      }

      $elements += @{
        type = 'shape'
        x = $x.x
        y = $x.y
        w = $x.w
        h = $x.h
        rot = $x.rot
        prst = $prst
        fill = $fill
        noFill = $noFill
        paragraphs = $paragraphs
      }
    }

    if ($node.LocalName -eq 'pic') {
      $pic = $node
      $spPr = $pic.SelectSingleNode('./p:spPr', $nsm)
      if (-not $spPr) { continue }

      $x = Get-Transform $spPr $nsm
      $blip = $pic.SelectSingleNode('./p:blipFill/a:blip', $nsm)
      $rid = ''
      if ($blip -and $blip.Attributes['r:embed']) { $rid = $blip.Attributes['r:embed'].Value }

      $target = ''
      if ($rid -and $relMap.ContainsKey($rid)) { $target = $relMap[$rid] }
      $target = ($target -replace '^\.\./media/', '')

      $elements += @{
        type = 'image'
        x = $x.x
        y = $x.y
        w = $x.w
        h = $x.h
        rot = $x.rot
        src = "$mediaBase/$target"
      }
    }
  }

  $slides += @{
    slide = [int]([regex]::Match($sf.BaseName, '\d+').Value)
    background = $bg
    elements = $elements
  }
}

$manifest = @{
  widthEmu = 12192000
  heightEmu = 6858000
  slides = $slides
}

$manifestPath = 'd:\VS project\cultural_technology\123\slides_manifest.json'
$manifest | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 $manifestPath

Write-Output "Manifest created: $manifestPath"
Write-Output "Slides: $($slides.Count)"
