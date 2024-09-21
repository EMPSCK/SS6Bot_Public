import re
text = 'ПлощА. Взр. 1/2. Бейсик Прод.\nГс. Калиничева Каринэ.\nЗгс. Васильева Марина, Завьялов Евгений, Сильде Владислав, Селиванова Ирина.\nЛинейные судьи: Андреев Леонид, Бойков Алексей, Горн Нина, Имреков Евгений, Карбаинов Михаил, Кораблева Надежда, Лебедев Александр, Привалова Галина, Приходько Алексей, Садчиков Павел, Сладкова Инга.\n\nПлощВ. Ю1 10т. 1/2. Прод.\nГс. Дурдина Елена.\nЗгс. Давиденко Евгений, Котелевец Геннадий, Морозов Алексей, Широких Лариса, Филиппов Владимир.\nЛинейные судьи: Асриян Ирина, Бисеров Александр, Боровский Андрей, Губарева Юлия, Гуськов Максим, Зайцева Елена, Колесник Константин, Кузюрина Любовь, Литюшкин Максим, Максимов Сергей, Нагов Вячеслав.'


async def get_parse(text, user_id):
    areas = re.split('\n\s{0,}\n', text)
    areas = [re.split('Гс.\s{0,}|Згс.\s{0,}|Линейные судьи\s{0,}:\s{0,}', i) for i in areas]
    areas = [[i[j].strip().strip('\n').strip('.') for j in range(len(i))] for i in areas]
    for areaindex in range(len(areas)):
        area = areas[areaindex]
        print(area[0])
        if areaindex == 0 and len(area) == 1 and ('ГСС' in area[0] or 'ГСек' in area[0]):
            area[0] = area[0].split('\n')
            for i in range(len(area[0])):
                area[0][i] = area[0][i].replace('ГСС. ', '')
                area[0][i] = area[0][i].replace('ГСек.', '')
                area[0][i] = area[0][i].strip().strip('.').strip('\n')
            otherjud = area[0]
            linjud = []
        else:
            linjud = re.split(',\s{0,}', area[-1])
            otherjud = re.split(',\s{0,}', ', '.join(
                [area[i] for i in range(len(area)) if i != 0 and area[i] != '' and i != len(area) - 1]))

get_parse(text)
