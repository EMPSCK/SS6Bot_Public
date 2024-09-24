import asyncio
import pymysql
async def filesmanager():
    while True:
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
        except:
            pass

filesmanager()