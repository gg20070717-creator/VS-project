import base64
import re
from pathlib import Path

html_path = Path('d:/VS project/cultural_technology/123/pre2_standalone.html')
html_path.chmod(0o666)
cont = html_path.read_text(encoding='utf-8')

img1_bg = base64.b64encode(Path('d:/VS project/cultural_technology/123/致歉.png').read_bytes()).decode('utf-8')
img2_bg = base64.b64encode(Path('d:/VS project/cultural_technology/123/水源极端发言.png').read_bytes()).decode('utf-8')
img3_bg = base64.b64encode(Path('d:/VS project/cultural_technology/123/上海宝爸大学.png').read_bytes()).decode('utf-8')

b64_str_1 = f"url('data:image/png;base64,{img1_bg}') center/cover no-repeat;"
b64_str_2 = f"url('data:image/png;base64,{img2_bg}') center/contain no-repeat;"
b64_str_3 = f"url('data:image/png;base64,{img3_bg}') center/contain no-repeat;"

new_cases = f"""
            if (slideNo === 6 && index === 0) {{
                htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: {b64_str_1}"></div><div class="ph-core"></div>';
            }}
            if (slideNo === 7 && index === 0) {{
                htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: {b64_str_2}"></div><div class="ph-core"></div>';
            }}
            if (slideNo === 8 && index === 0) {{
                htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: {b64_str_3}"></div><div class="ph-core"></div>';
            }}
"""

repl_func = r'(function appendImagePlaceholder\([^)]*\)\s*\{[\s\S]*?)(const slotWrapper = document\.createElement)'

def inj_func(m):
    return m.group(1) + new_cases + m.group(2)

cont = re.sub(repl_func, inj_func, cont)

cont = cont.replace('if (slideData.slide !== 1 && slideData.slide !== 2) {', 'if (slideData.slide !== 1 && slideData.slide !== 2 && slideData.slide !== 9 && slideData.slide !== 10) {')
cont = cont.replace('if (slideData.slide !== 1 && slideData.slide !== 2 && slideData.slide !== 9 && slideData.slide !== 10 && slideData.slide !== 9 && slideData.slide !== 10) {', 'if (slideData.slide !== 1 && slideData.slide !== 2 && slideData.slide !== 9 && slideData.slide !== 10) {')

html_path.write_text(cont, encoding='utf-8')
html_path.chmod(0o444)
print('Done!')
