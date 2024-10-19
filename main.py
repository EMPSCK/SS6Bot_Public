n, m = [int(x) for x in input().split()]
matrix = []
flag = 0
for i in range(m):
    matrix.append([int(x) for x in input().split()])


def check_sq(row, left, right):
    pass

#Проходимся по всем стрчкам матрицы начиная с 5
for rowindex in range(4, len(matrix)):
    # Определяем правый нижний угол квадрата
    for rightDownIndex in range(4, n):
        '''
        Перебираем левый нижний угол: если сочетание левого и правого углов равно стороне,
        отправляем в функцию на проверку квадрата (1 - квадрат с крестом, 2 - квадрат без креста, 0 - не квадрат)
        '''
        for leftDownIndex in range(0, rightDownIndex - 4):
            print(matrix[leftDownIndex: rightDownIndex + 1])
            if matrix[leftDownIndex: rightDownIndex + 1] == [1]*(leftDownIndex - rightDownIndex + 1):
                print(rowindex)
                if check_sq(rowindex, leftDownIndex, rightDownIndex) == 1:
                    flag = 1
                    pass
                elif check_sq(rowindex, leftDownIndex, rightDownIndex) == 2:
                    flag = 1
                    pass

if flag != 0:
    print('Квадрата нет')

for row in matrix:
    print(row)