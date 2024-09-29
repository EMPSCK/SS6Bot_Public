import re
a = 'Площ.А.. Финал.'
b = 'Площ.А. 1tttЮ2. 1/2 Финала.'

def get_area_num(text):
    group_id = re.search('\d+', text)
    print(group_id)


get_area_num(a)




