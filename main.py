n, m = [int(x) for x in input().split()]
matrix = []
flag = 0
for i in range(m):
    matrix.append([int(x) for x in input().split()])


def check_sq(row, left, right):
    a = right - left
    up = matrix[row - a][left: right + 1]
    if up != [1]*(a + 1):
        return 0

    leftSt = [matrix[i][left] for i in range(row - a, a + 1)]
    if leftSt != [1]*(a + 1):
        return 0

    rightSt = [matrix[i][right] for i in range(row - a, a + 1)]
    if rightSt != [1]*(a + 1):
        return 0

    body = [i[left + 1: right] for i in matrix[row - a + 1: row]]
    k = 0
    k1 = 0
    for i in range(len(body)):
        if body[i][k] == 1:
            k += 1

    for i in range(len(body)-1, -1, -1):
        if body[i][k1] == 1:
            k1 += 1

    if k1 == len(body) and k == len(body):
        return 2
    else:
        return 1



#Проходимся по всем стрчкам матрицы начиная с 5
for rowindex in range(4, len(matrix)):
    # Определяем правый нижний угол квадрата
    for rightDownIndex in range(4, n):
        '''
        Перебираем левый нижний угол: если сочетание левого и правого углов равно стороне,
        отправляем в функцию на проверку квадрата (1 - квадрат с крестом, 2 - квадрат без креста, 0 - не квадрат)
        '''
        if matrix[rowindex][rightDownIndex] == 1:
            for leftDownIndex in range(rightDownIndex - 4, -1, -1):
                if matrix[rowindex][leftDownIndex] == 0:
                    break
                if matrix[rowindex][leftDownIndex: rightDownIndex + 1] == [1]*(rightDownIndex - leftDownIndex + 1) and rowindex >= (rightDownIndex - leftDownIndex):
                    ans = check_sq(rowindex, leftDownIndex, rightDownIndex)
                    if ans == 1:
                        flag = 1
                        print('WIN, notmarked')
                    elif ans == 2:
                        flag = 1
                        print('WIN, marked')

if flag == 0:
    print('Квадрата нет')


