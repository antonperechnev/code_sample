# убираем лишние пробелы из строки, задание с отбора на стажировку тинькофф
import sys
st = sys.stdin.read()
good_st = ' '.join([i for i in st.split(' ') if i.isalpha()])
print(good_st, len(good_st))