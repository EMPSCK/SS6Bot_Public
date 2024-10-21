n, m = [int(x) for x in input().split()]
matrix = []
for i in range(m):
    matrix.append(input())


def check_sq(row, left, right):
    a = right - left
    up = matrix[row - a][left: right + 1]
    if up != '1'*(a + 1):
        return 0

    for i in range(row - a, row + 1):
        if matrix[i][left] != '1':
            return 0

    for i in range(row - a, row + 1):
        if matrix[i][right] != '1':
            return 0

    k = left + 1
    k1 = right - 1
    for rowb in range(row - a + 1, row):
        if matrix[rowb][k] != '1' or matrix[rowb][k1] != '1':
            return 1
        k += 1
        k1 -= 1

    return 2


def get_ans():
    # Проходимся по всем стрчкам матрицы начиная с 5
    flag = 0
    for rowindex in range(4, len(matrix)):
        # Определяем правый нижний угол квадрата
        for rightDownIndex in range(4, n):
            if matrix[rowindex][rightDownIndex] == '1':
                if matrix[rowindex][rightDownIndex - 4:rightDownIndex + 1] != '1' * (5):
                    continue

                for leftDownIndex in range(rightDownIndex - 4, -1, -1):
                    if matrix[rowindex][leftDownIndex] == '0':
                        break
                    if matrix[rowindex][leftDownIndex: rightDownIndex + 1] == '1' * (
                            rightDownIndex - leftDownIndex + 1) and rowindex >= (rightDownIndex - leftDownIndex):
                        ans = check_sq(rowindex, leftDownIndex, rightDownIndex)
                        if ans == 1:
                            flag = 1
                            return 'Not marked'
                        elif ans == 2:
                            flag = 1
                            return 'Marked'
                    else:
                        break
    if flag == 0:
        return 'Printing error'

print(get_ans())
