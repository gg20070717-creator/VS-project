import codecs, json

html_path = 'd:/VS project/cultural_technology/123/pre2_standalone.html'
with codecs.open(html_path, 'r', 'utf-8') as f:
    h = f.read()

# 1. Reverse the manifest changes
start_idx = h.find('const manifest = {')
end_idx = h.find('const deck = document.getElementById', start_idx)
if end_idx != -1:
    end_idx = h.rfind('}', start_idx, end_idx)

if start_idx != -1 and end_idx != -1:
    json_str = h[start_idx + len('const manifest = '):end_idx+1].strip()
    try:
        manifest = json.loads(json_str)
        
        # find the slide we injected (which became slide 3)
        to_delete = None
        for i, s in enumerate(manifest['slides']):
            if s.get('slide') == 3:
                texts = ''.join(r.get('text', '') for p in s.get('elements', [])[0].get('paragraphs', []) for r in p.get('runs', []))
                if '官方内部致歉' in texts:
                    to_delete = i
                    break
                    
        if to_delete is not None:
            del manifest['slides'][to_delete]
            
            # decremenet slide indices for everything > 2 (was 3)
            for s in manifest['slides']:
                if s.get('slide', 0) >= 3:
                    s['slide'] -= 1
                    
            new_json_str = json.dumps(manifest, ensure_ascii=False, indent=2)
            prefix = h[:start_idx] + 'const manifest = '
            suffix = h[end_idx+1:]
            
            # Ensure proper javascript format
            if not suffix.startswith(';'):
                suffix = ';' + suffix
            
            h = prefix + new_json_str + suffix
            print('Manifest reverted!')
        else:
            print('Could not find slide 3 to delete')
    except Exception as e:
        print('Error parsing manifest:', e)

import re
# Find the base64s we need for the correct mapping
def get_b64(marker):
    for b in re.finditer(r'base64,([a-zA-Z0-9+/=]+)', h):
        if b.group(1).startswith('iVBORw0KGgoAAAANSUhE' + marker):
            return b.group(1)
    return ""

b_img1 = get_b64('UgAAAyA')  # 424kb
b_img2 = get_b64('UgAABhg')  # 1MB
b_img3 = get_b64('UgAAA3s')  # 1.3MB
b_img4 = get_b64('UgAABGs')  # 391kb

def make_ph(b64, style='center center / cover'):
    return '<div class="ph-thumb" aria-hidden="true" style="background: url(\\\'data:image/png;base64,' + b64 + '\\\') ' + style + ' no-repeat;"></div><div class="ph-core"></div>'
def make_ph_card(b64):
    return '<div class="ph-thumb" aria-hidden="true" style="background: url(\\\'data:image/png;base64,' + b64 + '\\\') center/contain no-repeat; box-shadow: none; border-radius: 4px;"></div>'

# Now we rebuild the appendImagePlaceholder EXACTLY as it should be (without slide 3)
new_func = f"""function appendImagePlaceholder(layer, slot, slideNo, index) {{
          const ph = document.createElement('div');
          ph.className = 'elem img-placeholder';
          ph.style.left = `${{slot.x}}%`;
          ph.style.top = `${{slot.y}}%`;
          ph.style.width = `${{slot.w}}%`;
          ph.style.height = `${{slot.h}}%`;

          let htmlContent = '<div class="ph-thumb" aria-hidden="true"></div><div class="ph-core"></div>';

          if (slideNo === 3 && index === 0) {{
              htmlContent = '{make_ph(b_img2, "center/contain")}';
          }} else if (slideNo === 4) {{
              if (index === 0 || index === 1) {{
                  htmlContent = '{make_ph_card(b_img1)}';
              }}
          }} else if (slideNo === 5) {{
              if (index === 0) {{
                  htmlContent = '{make_ph(b_img3, "center/contain")}';
              }} else if (index === 1) {{
                  htmlContent = '{make_ph(b_img4, "center/contain")}';
              }}
          }}

          ph.innerHTML = htmlContent;
          layer.appendChild(ph);
      }}""".replace("'", '"')
      
# Wait, replacing ' with " might break string literals in JS if not careful.
# Let's just write the raw string and fix the quotes safely.
new_func = f"""function appendImagePlaceholder(layer, slot, slideNo, index) {{
          const ph = document.createElement('div');
          ph.className = 'elem img-placeholder';
          ph.style.left = `${{slot.x}}%`;
          ph.style.top = `${{slot.y}}%`;
          ph.style.width = `${{slot.w}}%`;
          ph.style.height = `${{slot.h}}%`;

          let htmlContent = '<div class=\"ph-thumb\" aria-hidden=\"true\"></div><div class=\"ph-core\"></div>';

          if (slideNo === 3 && index === 0) {{
              htmlContent = '<div class=\"ph-thumb\" aria-hidden=\"true\" style=\"background: url(\\'data:image/png;base64,{b_img2}\\') center/contain no-repeat;\"></div><div class=\"ph-core\"></div>';
          }} else if (slideNo === 4) {{
              if (index === 0 || index === 1) {{
                  htmlContent = '<div class=\"ph-thumb\" aria-hidden=\"true\" style=\"background: url(\\'data:image/png;base64,{b_img1}\\') center/contain no-repeat; box-shadow: none; border-radius: 4px;\"></div>';
              }}
          }} else if (slideNo === 5) {{
              if (index === 0) {{
                  htmlContent = '<div class=\"ph-thumb\" aria-hidden=\"true\" style=\"background: url(\\'data:image/png;base64,{b_img3}\\') center/contain no-repeat;\"></div><div class=\"ph-core\"></div>';
              }} else if (index === 1) {{
                  htmlContent = '<div class=\"ph-thumb\" aria-hidden=\"true\" style=\"background: url(\\'data:image/png;base64,{b_img4}\\') center/contain no-repeat;\"></div><div class=\"ph-core\"></div>';
              }}
          }}

          ph.innerHTML = htmlContent;
          layer.appendChild(ph);
      }}"""


idx = h.find('function appendImagePlaceholder(')
end_idx = h.find('function appendWeiboApp(', idx)
if end_idx == -1:
    end_idx = h.find('function createSlide(', idx)
end_func = h.rfind('}', idx, end_idx) + 1

if idx != -1 and end_func != -1:
    h = h[:idx] + new_func + h[end_func:]
    with codecs.open(html_path, 'w', 'utf-8') as f:
        f.write(h)
    print("Function reverted!")
else:
    print("Failed to replace function")

