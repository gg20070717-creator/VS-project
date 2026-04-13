import re

with open('d:/VS project/cultural_technology/123/pre2_standalone.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I see what happened. In inline_all.py, we replaced the json `"src": "ppt_xml_extracted/ppt/media/image12.png"`
# with `data:image/x;...`. This means inside the slideData json, elem.src is no longer '...image12.png',
# it's the base64 string. 
# 
# The regular expression `if (slideData.slide === 2 && /image12\.png|image13\.jpeg/i.test(elem.src || ''))`
# fails, because it's testing the base64 string for "image12.png" or "image13.jpeg".
# 
# So these two images are not given the class 'app-launch-icon' and are not clickable.
# 
# How to fix it? In the JSON, the elements also usually have an `x`, `y` position, but relying on that is fragile.
# Let's fix the logic that sets the app-launch-icon. 
# What if we just add a custom field to the JSON slideData before we replace the JSON?
# Or better, we can modify the JavaScript logic:
# instead of `/image12\.png|image13\.jpeg/i.test(elem.src || '')`
# we can identify them by their positions, or we can restore the file name in a custom attribute `elem.originalSrc`.
# 
# Let's just fix the javascript function in the standalone file. Since we can't easily rely on the data string, let's identify them by image size/position, OR by checking if it's the 1st / 2nd image created on Slide 2.

func_pattern = r"const img = document\.createElement\('img'\);\s+img\.className = 'elem img';\s+img\.loading = 'eager';\s+img\.decoding = 'async';\s+img\.src = elem\.src;\s+if \(slideData\.slide === 2 && /image12\\\.png\|image13\\\.jpeg/i\.test\(elem\.src \|\| ''\)\) \{"

replacement = """const img = document.createElement('img');
          img.className = 'elem img';
          img.loading = 'eager';
          img.decoding = 'async';
          img.src = elem.src;
          
          // FIX: In the standalone base64 version, elem.src is a base64 string.
          // image12 (shuiyuan) has w: 609600, h: 609600
          // image13 (xiaohongshu) has w: 609600, h: 609600
          // Both are positioned at y: 3657600
          if (slideData.slide === 2 && elem.w === 609600 && elem.h === 609600 && elem.y === 3657600) {
              if (elem.x === 9601200) { // image13 xiaohongshu
                  img.classList.add('app-launch-icon');
                  img.dataset.appId = 'xiaohongshu';
                  img.style.borderRadius = '16px'; 
                  img.style.boxShadow = '0 6px 16px rgba(0,0,0,0.1)';
              } else if (elem.x === 7650893) { // image12 shuiyuan
                  img.classList.add('app-launch-icon');
                  img.dataset.appId = 'shuiyuan';
                  img.style.borderRadius = '16px';
                  img.style.boxShadow = '0 6px 16px rgba(0,0,0,0.1)';
              }
          }
          
          if (slideData.slide === 2 && /image12\\.png|image13\\.jpeg/i.test(elem.src || '')) {
"""

if re.search(func_pattern, content):
    print("Found exact pattern!")
else:
    print("Pattern not found! Trying alternative...")
    # Alternative replace
    target = "img.src = elem.src;\n\n                    if (slideData.slide === 2 && /image12\\.png|image13\\.jpeg/i.test(elem.src || '')) {"
    if target in content:
        content = content.replace(target, target.replace(
            "img.src = elem.src;", 
            """img.src = elem.src;
                    if (slideData.slide === 2 && elem.y === 3657600 && elem.w === 609600) {
                        img.classList.add('app-launch-icon');
                        img.dataset.appId = elem.x > 8000000 ? 'xiaohongshu' : 'shuiyuan';
                        img.style.borderRadius = '15%';
                        img.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)';
                        img.style.objectFit = 'cover';
                    }
            """
        ))
        print("Patched via literal replace!")

with open('d:/VS project/cultural_technology/123/pre2_standalone.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to standalone HTML!")
