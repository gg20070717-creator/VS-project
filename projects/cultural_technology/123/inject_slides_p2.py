import base64
import codecs
from pathlib import Path

dir_path = Path(r'd:/VS project/cultural_technology/123/')
files = {
    'zhiqian': '致歉.png',
    'shuiyuan': '水源极端发言.png',
    'baoba': '上海宝爸大学.png'
}

b64_data = {}
for k, v in files.items():
    with open(dir_path / v, 'rb') as img:
        b64_data[k] = base64.b64encode(img.read()).decode('utf-8')

html_path = dir_path / 'pre2_standalone.html'
content = html_path.read_text(encoding='utf-8')

# Change 1: skip placeholder generation for 9 and 10
fn_start = 'function appendImagePlaceholder(layer, slot, slideNo, index) {'
idx1 = content.find(fn_start)
if idx1 == -1:
    raise SystemExit("appendImagePlaceholder not found")

insertion_idx = idx1 + len(fn_start)
new_content = content[:insertion_idx] + '\n          if (slideNo === 9 || slideNo === 10) return;' + content[insertion_idx:]

# Update content after first change
content = new_content

# Change 2: Inject new placeholders
idx_insert = content.find('ph.innerHTML = htmlContent;')
if idx_insert == -1:
    raise SystemExit("ph.innerHTML assignment not found")

new_code = f'''
          if (slideNo === 6 && index === 1) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['zhiqian']}\\') center/contain no-repeat;"></div><div class="ph-core"></div>';
          }}
          if (slideNo === 7 && index === 0) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['shuiyuan']}\\') center/contain no-repeat;"></div><div class="ph-core"></div>';
          }}
          if (slideNo === 8 && index === 0) {{
              htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64_data['baoba']}\\') center/contain no-repeat;"></div><div class="ph-core"></div>';
          }}
'''
final_content = content[:idx_insert] + new_code + content[idx_insert:]

# Remove read-only if necessary, then write
import os, stat
os.chmod(html_path, stat.S_IWRITE)
html_path.write_text(final_content, encoding='utf-8')
print('Successfully injected new slides and removed 9 & 10.')
