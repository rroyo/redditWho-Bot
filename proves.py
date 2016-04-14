i = 0
a = []

while i < 10:
    a.append(i)
    i += 1

print(a)


class SURT():
    'Una prova'

for n in a:
    try:
        if (n == 4):
            raise BaseException
        print(n)        
    except BaseException as e:
        print('He sortit')
        


