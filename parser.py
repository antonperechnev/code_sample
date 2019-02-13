import requests
from bs4 import BeautifulSoup
from datetime import datetime

#  этот кусок берет данные и запихивает их в список, нужно сделать через генератор списков и обобщить
def data_lst(x):
    data = []
    data_set = table[x]
    for i in data_set:
        try:
            if i.get_text()[0].isalpha():
                data.append(datetime.strptime(i.get_text().replace(',', ''), '%b %d %Y'))
                continue
            data.append(float(i.get_text().replace(',', '')))
        except AttributeError:
            pass
    return(data)



url = 'https://coinmarketcap.com/currencies/maker/historical-data/?start=20130428&end=20190211'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find_all('tr', class_="text-right")
#for i in range(len(table)): #работает прогоняет по всем датам, но надо все в один список
#    print(data_lst(i))
print(data_lst(0))
