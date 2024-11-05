"""
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
"""
import requests

# Ваш токен бота
BOT_TOKEN = '7217667401:AAGoDN0XJmwqAAnBstZHg1wO1hcgQjpDXqU'

# Идентификатор канала (может быть либо username, либо chat_id)
CHANNEL_ID = '@helloworldqwertyuiop'

# Ограничение на количество использований ссылки
MEMBER_LIMIT = 1

# Время жизни ссылки в секундах (например, 1800 секунд = 30 минут)
EXPIRATION_TIME = 1800

def generate_invite_link(bot_token, channel_id, member_limit, expiration_time):
    url = f"https://api.telegram.org/bot{bot_token}/exportChatInviteLink"
    payload = {
        "chat_id": channel_id,
        "member_limit": member_limit,
        "expire_date": expiration_time
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        raise Exception(f"Ошибка при генерации ссылки: {response.text}")

if __name__ == "__main__":
    try:
        link = generate_invite_link(BOT_TOKEN, CHANNEL_ID, MEMBER_LIMIT, EXPIRATION_TIME)
        print(f"Временная ссылка на канал: {link}")
    except Exception as e:
        print(e)