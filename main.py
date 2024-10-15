import re
text = "Картинка <img src='bg.jpg'> в тексте</p>"
match = re.findall(r"<(img\s+[^>]*)src=[\"'](.+?)[\"']", text)
print(match)
