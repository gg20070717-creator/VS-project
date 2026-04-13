import codecs, json, re, base64

html_path = 'd:/VS project/cultural_technology/123/pre2_standalone.html'
with codecs.open(html_path, 'r', 'utf-8') as f:
    html = f.read()

match = re.search(r'(const\s+manifest\s*=\s*)({.*?\n\s+});', html, flags=re.DOTALL)
if match:
    prefix = match.group(1)
    json_str = match.group(2)
    # the last property has unquoted keys maybe? No, it's valid JSON.
    try:
        manifest = json.loads(json_str)
        print("Manifest loaded successfully")
        
        # We want to insert slide 3
        
        new_slide = {
            "background": {
                "alpha": 1,
                "hex": "F0F5F5"
            },
            "elements": [
                {
                    "x": 762000,
                    "type": "shape",
                    "paragraphs": [
                        {
                            "runs": [
                                {
                                    "sz": 3600,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": True,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "官方内部致歉",
                                    "i": False
                                }
                            ],
                            "align": "l"
                        }
                    ],
                    "rot": 0,
                    "y": 635000,
                    "w": 8051800,
                    "noFill": True,
                    "h": 508000,
                    "prst": "rect"
                },
                {
                    "x": 762000,
                    "type": "shape",
                    "paragraphs": [
                        {
                            "runs": [
                                {
                                    "sz": 2000,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": False,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "水源团队近期在处理“校庆微电影争议”事件时，未能顾及全体师生的感受，甚至出现了部分不妥言论，对此我们深感抱歉。",
                                    "i": False
                                }
                            ],
                            "align": "l"
                        },
                        {
                            "runs": [
                                {
                                    "sz": 2000,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": False,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "我们目前正全面审查内部审核流程，并已对相关责任人进行处理。我们将吸取教训，加强团队内部管理和审查，坚决避免类似事件再次发生。",
                                    "i": False
                                }
                            ],
                            "align": "l"
                        },
                         {
                            "runs": [{
                                "text": " "
                            }]
                         },
                        {
                            "runs": [
                                {
                                    "sz": 2000,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": False,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "感谢全校师生的监督与批评，我们会以此为戒，尽全力降低影响。",
                                    "i": False
                                }
                            ],
                            "align": "l"
                        }
                    ],
                    "rot": 0,
                    "y": 1450000,
                    "w": 6500000,
                    "noFill": True,
                    "h": 3000000,
                    "prst": "rect",
                },
                {
                    "x": 7000000,
                    "type": "shape",
                    "paragraphs": [
                        {
                            "runs": [
                                {
                                    "sz": 1800,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": True,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "上海交通大学融媒体中心",
                                    "i": False
                                }
                            ],
                            "align": "r"
                        },
                        {
                            "runs": [
                                {
                                    "sz": 1800,
                                    "color": {
                                        "alpha": 1,
                                        "hex": "2F4F4F"
                                    },
                                    "b": True,
                                    "spc": 0,
                                    "font": "Noto Sans SC",
                                    "text": "2026年4月1日",
                                    "i": False
                                }
                            ],
                            "align": "r"
                        }
                    ],
                    "rot": 0,
                    "y": 4800000,
                    "w": 4000000,
                    "noFill": True,
                    "h": 1000000,
                    "prst": "rect",
                },
                {
                    "x": 8000000,
                    "type": "shape",
                    "rot": 0,
                    "y": 1450000,
                    "w": 3429000,
                    "noFill": True,
                    "h": 3429000,
                    "prst": "rect",
                    "phType": "pic"
                }
            ],
            "slide": 3
        }

        # increment slides
        for s in manifest['slides']:
            if s.get('slide', 0) >= 3:
                s['slide'] += 1
                
        # insert new slide
        manifest['slides'].insert(2, new_slide)
        
        new_json_str = json.dumps(manifest, ensure_ascii=False, indent=2)
        html = html[:match.start()] + prefix + new_json_str + ";" + html[match.end():]
        print("Manifest replaced.")
    except Exception as e:
        print("Error parsing json:", e)
else:
    print("Could not find manifest")

# Now handle the base64 injection for 致歉.png
with open('d:/VS project/cultural_technology/123/致歉.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

# Shift the conditionals in appendImagePlaceholder
html = re.sub(r'slideNo === 6', 'slideNo === 7', html)
html = re.sub(r'slideNo === 5', 'slideNo === 6', html)
html = re.sub(r'slideNo === 4', 'slideNo === 5', html)
html = re.sub(r'slideNo === 3', 'slideNo === 4', html)

# Insert the new slideNo === 3 conditional
new_cond = f'''if (slideNo === 3) {{
              if (index === 0) {{
                  htmlContent = '<div class="ph-thumb" aria-hidden="true" style="background: url(\\'data:image/png;base64,{b64}\\') center center / cover no-repeat;"></div><div class="ph-core"></div>';
              }}
          }}
          '''

# Find the start of the conditionals (which are now slideNo === 5, etc)
replace_idx = html.find('if (slideNo === 5)')
if replace_idx != -1:
    html = html[:replace_idx] + new_cond + html[replace_idx:]
    print("Injected base64 logic.")

with codecs.open(html_path, 'w', 'utf-8') as f:
    f.write(html)
print("Done writing.")
