#интерфейс для работы с классами
import os
import tempfile


class File:
    def __init__(self, file_name, current=0):
        self.file_name = file_name
        self.current = current

    def write(self, some_line):
        with open(self.file_name, 'a+') as f:
            f.write(some_line + '\n')

    def __add__(self, other):
        new_path = os.path.join(tempfile.gettempdir(), 'add.txt')#файл создается в папке temp
        a: str = open(self.file_name).read()
        b: str = open(other.file_name).read()
        with open(new_path, 'a+') as d:
            d.write(a + ' ')
            d.write(b + '\n')

    def __iter__(self):
        return self

    def __next__(self):
        h = open(self.file_name).read().split('\n')
        a = len(h[:-1])
        if self.current > a:
            raise StopIteration
        result = h[self.current]
        self.current += 1
        return result

    def __str__(self):
        return self.file_name

#тесты
#d = File(r'E:\anton\t.txt')
#c = File(r'E:\anton\t.txt')
#print(c)
#c.write('no no no')
#h = open(c.file_name).read()
#print(h.split('\n'))
#v = d + c
#for i in c:
#    print('this is str {}'.format(i))
#print(v)
