lst_of_log = []
with open('input1.txt') as f:
    f.read(2)
    days = int(f.read(1))
    f.seek(6)
    for i in f.readlines():
        lst_of_log.append(i.split(' '))
for i in lst_of_log:
    i[1] = int(i[1])
    i[2] = int(i[2])
dict_of_days = {}
for i in lst_of_log:
    if i[0] == 'arrival':
        if i[1] in dict_of_days:
            dict_of_days[i[1]] = dict_of_days[i[1]] + i[2]
        else:
            dict_of_days[i[1]] = i[2]
    else:
        if i[1] in dict_of_days:
            i[2] = - i[2]
            dict_of_days[i[1]] = dict_of_days[i[1]] + i[2]
        else:
            dict_of_days[i[1]] = - i[2]
list_of_days = sorted(list(dict_of_days.items()), key=lambda x: x[0])
peoples = 0
day = 1
odd_day = []
even_day = []
for i in list_of_days:
    if day > days: break
    peoples += i[1]
    if day % 2 == 0:
        even_day.append(peoples)
        day += 1
    else:
        odd_day.append(peoples)
        day += 1
print(f'{max(odd_day)} {max(even_day)}')





#print(f'{max(Mefody)} {max(Kirill)}')
#print(dict_of_days)