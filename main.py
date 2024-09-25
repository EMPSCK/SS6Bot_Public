import re
lastname = re.search('^[А-ЯA-Z][а-яa-z]*', 'БулатовАртем')
print(lastname)