import re

with open('d:/VS project/cultural_technology/123/pre2.backup.before-advanced-transitions.html', 'r', encoding='utf-8') as f:
    text = f.read()

# The incorrect code currently looks like:
# ph.style.left = \%;
# we need to replace it with:
# ph.style.left = \\%\;

text = text.replace('ph.style.left = %;', 'ph.style.left = ${slot.x}%;')
text = text.replace('ph.style.top = %;', 'ph.style.top = ${slot.y}%;')
text = text.replace('ph.style.width = %;', 'ph.style.width = ${slot.w}%;')
text = text.replace('ph.style.height = %;', 'ph.style.height = ${slot.h}%;')

with open('d:/VS project/cultural_technology/123/pre2.backup.before-advanced-transitions.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed syntax errors!")
