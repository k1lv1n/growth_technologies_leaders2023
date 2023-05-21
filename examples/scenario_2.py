"""
Сценарий 2. 2 спутнкиа, по 1 съемке и по 2 передачи на каждого. Без конфликтов.
"""

new_table = {}
is_opened = {}

for el in timeline:
    print('curr el:', el)
    if el[1] not in new_table.keys():
        new_table[el[1]] = [{'Begin': el[0], 'End': None}]
        is_opened[el[1]] = True
        
    print('old table:', new_table)
    opened = [i for i in is_opened.items() if i[1]]
    if not is_opened[el[1]]:
        is_opened[el[1]] = True
        new_table[el[1]].append({'Begin': el[0], 'End': None})

    # Добавляем точки к открытым таймлайнам
    for opened_el in opened:
        if new_table[opened_el[0]][-1]['Begin'] != el[0]:
            new_table[opened_el[0]][-1]['End'] = el[0]
            if opened_el[0] != el[1]:
                new_table[opened_el[0]].append({'Begin': el[0], 'End': None})
            else:
                is_opened[el[1]] = False