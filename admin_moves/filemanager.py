import pymysql
import config
import asyncio
import os
import requests

async def compid_to_chairman(compid):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"SELECT chairman_Id from competition where compid = {compid}")
            ans = cur.fetchone()
            return ans['chairman_Id']
    except:
        return 0

async def filesmanager(bot):
    while True:
        print("Я тут")
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            # Чистим таблицу со старыми копиями, заполняем ее новыми
            cur = conn.cursor()
            cur.execute("DELETE FROM competition_files_copy")
            conn.commit()
            cur.execute("INSERT INTO competition_files_copy SELECT * FROM competition_files")
            conn.commit()
            cur.execute("SELECT * FROM competition_files")
            ans = cur.fetchall()
            for file in ans:
                url = file['loadUrl']
                compid = file['compId']
                delurl = file['deleteUrl']
                chairman_id = await  compid_to_chairman(compid)

                response = requests.get(url)
                if response.status_code == 200:
                    file = open(f"Analytics_{compid}.pdf", 'wb')
                    file.write(response.content)
                    file.close()
                    os.remove(f"Analytics_{compid}.pdf")
                    await bot.send_message(chairman_id, 'Вот этот ебучий файл')
                    #response = requests.get(delurl)
                    #cur.execute(f"DELETE FROM competition_files WHERE compId = {compid}")
                else:
                    await bot.send_message(config.ADMIN_ID, f"compId: {compid}\nНе получилось скачать файл")
        print('Я все')
        await asyncio.sleep(60)
