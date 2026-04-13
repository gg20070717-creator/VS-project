import re

with open('d:/VS project/cultural_technology/123/pre2_standalone.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = "img.src = elem.src;\n\n                    if (slideData.slide === 2 && /image12\\.png|image13\\.jpeg/i.test(elem.src || '')) {"

if target in content:
    content = content.replace(target, """img.src = elem.src;
                    if (slideData.slide === 2 && elem.y === 3657600 && elem.w === 609600) {
                        img.classList.add('app-launch-icon');
                        img.dataset.appId = elem.x > 8000000 ? 'xiaohongshu' : 'shuiyuan';
                        img.style.borderRadius = '20%';
                        img.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
                    }
                    if (slideData.slide === 2 && /image12\\.png|image13\\.jpeg/i.test(elem.src || '')) {""")
    print("Patched successfully!")
else:
    print("Failed to find target in standalone HTML.")

with open('d:/VS project/cultural_technology/123/pre2_standalone.html', 'w', encoding='utf-8') as f:
    f.write(content)
