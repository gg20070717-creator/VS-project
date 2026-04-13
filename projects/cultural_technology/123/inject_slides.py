import base64
import codecs

dir_path = 'd:/VS project/cultural_technology/123/'
files = {
    'xiaopai': '校牌.png',
    'dangshiren': '当事人发言.png',
    'zhuliu': '主流媒体讨论.png'
}

b64_data = {}
for k, v in files.items():
    with open(dir_path + v, 'rb') as img:
        b64_data[k] = base64.b64encode(img.read()).decode('utf-8')

html_path = dir_path + 'pre2_standalone.html'
with codecs.open(html_path, 'r', 'utf-8') as f:
    content = f.read()

idx1 = content.find('if (slideNo === 4) {')
idx2 = content.find('          ph.innerHTML = htmlContent;', idx1)

if idx1 != -1 and idx2 != -1:
    old_block = content[idx1:idx2]
    new_block = old_block + f'''
          if (slideNo === 3 && index === 0) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['xiaopai']}\\') center/contain no-repeat;"></div><div class="ph-core"><div class="ph-icon">+</div><div>查看完整图片</div></div>';
          }}
          if (slideNo === 5 && index === 0) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['dangshiren']}\\') center/contain no-repeat;"></div><div class="ph-core"><div class="ph-icon">+</div><div>查看完整图片</div></div>';
          }}
          if (slideNo === 6 && index === 0) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['zhuliu']}\\') center/contain no-repeat;"></div><div class="ph-core"><div class="ph-icon">+</div><div>查看完整图片</div></div>';
          }}
'''
    new_content = content[:idx1] + new_block + content[idx2:]
    with codecs.open(html_path, 'w', 'utf-8') as f:
        f.write(new_content)
    print('Successfully inserted new slide conditionals.')
else:
    print('Could not find injection point.', idx1, idx2)
