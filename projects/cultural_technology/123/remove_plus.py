import codecs

path = 'd:/VS project/cultural_technology/123/pre2_standalone.html'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

new_content = content.replace('<div class=\\"ph-icon\\">+</div>', '')

if content != new_content:
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(new_content)
    print('Replaced successfully.')
else:
    print('String not found.')
