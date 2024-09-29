import pymysql
import config
from queries import general_queries
from chairman_moves import check_list_judges
import re
import datetime
from datetime import date

async def set_active_comp_for_chairman(tg_id, id):
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
            cur.execute(f"UPDATE skatebotusers SET id_active_comp = {id} WHERE tg_id = {tg_id}")
            conn.commit()
            cur.close()
            return 1
    except:
        print('Ошибка выполнения запроса на установку соревнований')
        return 0


async def get_Scrutineer(tg_id):
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
            active_comp_id = await general_queries.get_CompId(tg_id)
            cur.execute(f"SELECT scrutineerId FROM competition WHERE compId = {active_comp_id}")
            scrutinner_id = cur.fetchone()
            cur.close()
            return scrutinner_id['scrutineerId']
    except:
        print('Ошибка выполнения запроса поиск scrutinner для chairman')
        return 0


async def get_list_comp(tg_id):
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
            cur.execute(f"SELECT compName, compId, city, date1, date2 FROM competition WHERE chairman_id = {tg_id} and isActive = 1")
            competitions = cur.fetchall()
            cur.close()
            ans = []
            now = date.today()
            for comp in competitions:
                a = now - comp['date2']
                if a.days <= 0:
                    ans.append(comp)
            return ans
    except:
        print('Ошибка выполнения запроса на поиск соревнований для chairman1')
        return 0

async def set_free_judges(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            for i in config.judges_index[user_id]:
                cur.execute(f"UPDATE competition_judges SET is_use = 1 WHERE lastName = '{i[0]}' AND firstName = '{i[1]}' AND bookNumber = {i[2]} AND compId = {active_comp}")
                conn.commit()

            cur.close()
            return 1
    except:
        print('Ошибка выполнения запроса на установку свободных судей')
        return 0

async def get_free_judges(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            judges_use = config.judges_index[user_id]
            cur.execute(f"SELECT * FROM competition_judges WHERE compId = {active_comp} AND is_use = 0 ORDER BY lastName")
            judgesComp = cur.fetchall()
            cur.close()

            #Если судьи не загружены на турнир
            if judgesComp == ():
                return 'свободных судей нет'
            judges_free = judgesComp.copy()
            for jud in judgesComp:
                for jud1 in judges_use:
                    if jud['firstName'] == jud1[1] and jud['lastName'] == jud1[0]:
                        judges_free.remove(jud)
            if judges_free == []:
                return 'свободных судей нет'

            judges_free = ', '.join([i['lastName'] + ' ' + i['firstName'] for i in judges_free])

            return judges_free

    except Exception as e:
        print(e)
        print('Ошибка выполнения запроса на установку свободных судей')
        return 0


async def set_problem_jud_as_is(user_id, jud, booknumber=-1):
    try:
        active_comp = await general_queries.get_CompId(user_id)
        jud = jud.split()
        if len(jud) == 2:
            firstname = jud[1]
            lastname = jud[0]
        else:
            lastname = jud[0]
            firstname = ' '.join(jud[1::])
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        notjud = re.match(r'^[a-zA-Z]+\Z', firstname.replace(' ', '')) is not None
        with conn:
            cur = conn.cursor()
            # Если судья уже есть в таблице competition_judges
            cur.execute(
                f"DELETE FROM competition_judges WHERE ((firstName = '{firstname}' AND lastName = '{lastname}') OR (firstName2 = '{firstname}' AND lastName2 = '{lastname}')) AND compId = {active_comp}")
            conn.commit()

            person = None
            if booknumber != -1:
                cur.execute(f"SELECT * FROM judges WHERE BookNumber = {booknumber}")
                person = cur.fetchone()
            if person is not None:
                lastname1 = person['LastName']
                firstname1 = person['FirstName']
                BookNumber = person['BookNumber']
                SecondName = person['SecondName']
                Birth = person['Birth']
                DSFARR_Category = person['DSFARR_Category']
                DSFARR_CategoryDate = person['DSFARR_CategoryDate']
                WDSF_CategoryDate = person['WDSF_CategoryDate']
                RegionId = person['RegionId']
                City = person['City']
                Club = person['Club']
                Translit = person['Translit']
                Archive = person['Archive']
                SPORT_Category = person['SPORT_Category']
                SPORT_CategoryDate = person['SPORT_CategoryDate']
                SPORT_CategoryDateConfirm = person['SPORT_CategoryDateConfirm']
                federation = person['federation']
                sql = "INSERT INTO competition_judges (`compId`, `lastName`, `firstName`, `SecondName`, `Birth`, `DSFARR_Category`, `DSFARR_CategoryDate`, `WDSF_CategoryDate`, `RegionId`, `City`, `Club`, `Translit`, `SPORT_Category`, `SPORT_CategoryDate`, `SPORT_CategoryDateConfirm`, `federation`, `Archive`, `bookNumber`, `notJudges`, `is_use`, `lastName2`, `firstName2`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (
                    active_comp, lastname1, firstname1, SecondName, Birth, DSFARR_Category, DSFARR_CategoryDate,
                    WDSF_CategoryDate,
                    RegionId, City, Club, Translit, SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm,
                    federation, Archive, BookNumber, notjud, 0, lastname, firstname))
                conn.commit()
            else:
                sql = "INSERT INTO competition_judges (`compId`, `lastName`, `firstName`, `notJudges`, `is_use`, `bookNumber`, `lastName2`, `firstName2`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (active_comp, lastname, firstname, notjud, 0, booknumber, lastname, firstname))
                conn.commit()
        cur.close()
        return 1
    except Exception as e:
        print(e)
        print('Ошибка выполнения запроса на установку проблемных судей')
        return 0

async def set_problem_jud_as_is_1(user_id, jud, name=''):
    try:
        print(jud, name)
        bn = 0
        if name != '':
            i, bn = name.split('|')
            i = i.split()
            bn = int(bn)
            if len(i) == 2:
                lastname2 = i[0]
                firstname2 = i[1]
            else:
                lastname2 = i[0]
                firstname2 = ' '.join(i[1::])
        active_comp = await general_queries.get_CompId(user_id)
        jud = jud.split()
        if len(jud) == 2:
            firstname = jud[1]
            lastname = jud[0]
        else:
            lastname = jud[0]
            firstname = ' '.join(jud[1::])

        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        notjud = re.match(r'^[a-zA-Z]+\Z', firstname.replace(' ', '')) is not None
        with conn:
            cur = conn.cursor()
            if bn != 0:
                cur.execute(f"SELECT * FROM judges WHERE BookNumber = {bn}")
            else:
                cur.execute(
                    f"SELECT * FROM judges WHERE FirstName = '{firstname}' AND LastName = '{lastname}'")
            person = cur.fetchone()
            BookNumber = person['BookNumber']
            SecondName = person['SecondName']
            Birth = person['Birth']
            DSFARR_Category = person['DSFARR_Category']
            DSFARR_CategoryDate = person['DSFARR_CategoryDate']
            WDSF_CategoryDate = person['WDSF_CategoryDate']
            RegionId = person['RegionId']
            City = person['City']
            Club = person['Club']
            Translit = person['Translit']
            Archive = person['Archive']
            SPORT_Category = person['SPORT_Category']
            SPORT_CategoryDate = person['SPORT_CategoryDate']
            SPORT_CategoryDateConfirm = person['SPORT_CategoryDateConfirm']
            federation = person['federation']
            # Если судья уже есть в таблице competition_judges
            cur.execute(
                f"DELETE FROM competition_judges  WHERE firstName2 = '{firstname}' AND lastName2 = '{lastname}' AND compId = {active_comp}")
            conn.commit()

            if name != '':
                sql = "INSERT INTO competition_judges (`compId`, `lastName`, `firstName`, `SecondName`, `Birth`, `DSFARR_Category`, `DSFARR_CategoryDate`, `WDSF_CategoryDate`, `RegionId`, `City`, `Club`, `Translit`, `SPORT_Category`, `SPORT_CategoryDate`, `SPORT_CategoryDateConfirm`, `federation`, `Archive`, `bookNumber`, `notJudges`, `is_use`, `firstName2`, `lastName2`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (
                    active_comp, lastname, firstname, SecondName, Birth, DSFARR_Category, DSFARR_CategoryDate,
                    WDSF_CategoryDate,
                    RegionId, City, Club, Translit, SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm,
                    federation, Archive, BookNumber, notjud, 0, firstname2, lastname2))
                conn.commit()
            else:
                sql = "INSERT INTO competition_judges (`compId`, `lastName`, `firstName`, `SecondName`, `Birth`, `DSFARR_Category`, `DSFARR_CategoryDate`, `WDSF_CategoryDate`, `RegionId`, `City`, `Club`, `Translit`, `SPORT_Category`, `SPORT_CategoryDate`, `SPORT_CategoryDateConfirm`, `federation`, `Archive`, `bookNumber`, `notJudges`, `is_use`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (
                    active_comp, lastname, firstname, SecondName, Birth, DSFARR_Category, DSFARR_CategoryDate,
                    WDSF_CategoryDate,
                    RegionId, City, Club, Translit, SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm,
                    federation, Archive, BookNumber, notjud, 0))
                conn.commit()
            cur.close()
            return 1
    except Exception as e:
        print(e)
        print('Ошибка выполнения запроса на установку проблемных судей')
        return 0


async def cancel_load(user_id):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        active_comp = await general_queries.get_CompId(user_id)
        with conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM competition_judges WHERE compId = {active_comp}")
            conn.commit()
        return 1
    except:
        return 0


async def get_similar_judges(jud):
    try:
        similar_judges = []
        jud = jud.split()
        if len(jud) == 2:
            firstname = set(jud[1])
            lastname = set(jud[0])
        else:
            lastname = set(jud[0])
            firstname = set(' '.join(jud[1::]))

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
            cur.execute(f"SELECT * FROM judges")
            judges = cur.fetchall()
            for el in judges:
                elfirstname = el['FirstName']
                ellastname = el['LastName']
                elbboknumber = el['BookNumber']
                if len(set(firstname).symmetric_difference(set(elfirstname))) + len(set(lastname).symmetric_difference(set(ellastname))) <= 4:
                    similar_judges.append(el)
            cur.close()
            return similar_judges
    except:
        return 0

async def add_problemcorrect_jud(booknumber, user_id, name2):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        i = name2.split()
        if len(i) == 2:
            lastname2, firstname2 = i[0], i[1]
        else:
            lastname2 = i[0]
            firstname2 = ' '.join(i[1::])

        active_comp = await general_queries.get_CompId(user_id)
        with conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM judges WHERE BookNumber = {booknumber}")
            person = cur.fetchall()
            last_name = person[0]['LastName']
            name = person[0]['FirstName']
            SecondName = person[0]['SecondName']
            Birth = person[0]['Birth']
            DSFARR_Category = person[0]['DSFARR_Category']
            DSFARR_CategoryDate = person[0]['DSFARR_CategoryDate']
            WDSF_CategoryDate = person[0]['WDSF_CategoryDate']
            RegionId = person[0]['RegionId']
            City = person[0]['City']
            Club = person[0]['Club']
            Translit = person[0]['Translit']
            Archive = person[0]['Archive']
            SPORT_Category = person[0]['SPORT_Category']
            SPORT_CategoryDate = person[0]['SPORT_CategoryDate']
            SPORT_CategoryDateConfirm = person[0]['SPORT_CategoryDateConfirm']
            federation = person[0]['federation']
            notjud = re.match(r'^[a-zA-Z]+\Z', name.replace(' ', '')) is not None

            # Если судья уже есть в таблице competition_judges
            cur.execute(
                f"DELETE FROM competition_judges WHERE firstName2 = '{firstname2}' AND lastName2 = '{lastname2}' AND compId = {active_comp}")
            conn.commit()

            sql = "INSERT INTO competition_judges (`compId`, `lastName`, `firstName`, `SecondName`, `Birth`, `DSFARR_Category`, `DSFARR_CategoryDate`, `WDSF_CategoryDate`, `RegionId`, `City`, `Club`, `Translit`, `SPORT_Category`, `SPORT_CategoryDate`, `SPORT_CategoryDateConfirm`, `federation`, `Archive`, `bookNumber`, `notJudges`, `is_use`, `firstName2`, `lastName2`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (
                active_comp, last_name, name, SecondName, Birth, DSFARR_Category, DSFARR_CategoryDate,
                WDSF_CategoryDate,
                RegionId, City, Club, Translit, SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm,
                federation, Archive, booknumber, notjud, 0, firstname2, lastname2))
            conn.commit()
    except Exception as e:
        print(e)
        return 0

async def for_free(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
        name = await general_queries.CompId_to_name(active_comp)
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
            cur.execute(f"SELECT * FROM competition_judges WHERE compId = {active_comp} AND is_use = 0 ORDER BY lastName")
            judgesComp = cur.fetchall()
            cur.close()

            #Если судьи не загружены на турнир
            if judgesComp == ():
                return 'Свободных судей нет'
            judges_free = name + '\n\n' +'\n'.join([i['lastName'] + ' ' + i['firstName'] + ', ' + str(i['City']) for i in judgesComp])
            return judges_free

    except Exception as e:
        print(e)
        print('Ошибка выполнения запроса for_free')
        return 0



async def get_similar_lin_judges(jud, user_id):
    try:
        similar_judges = []
        lastname, firstname = jud
        active_comp = await general_queries.get_CompId(user_id)

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
            cur.execute(f"SELECT * FROM competition_judges WHERE compId = {active_comp}")
            judges = cur.fetchall()
            for el in judges:
                elfirstname = el['firstName']
                ellastname = el['lastName']
                elbboknumber = el['bookNumber']
                if len(set(firstname).symmetric_difference(set(elfirstname))) + len(set(lastname).symmetric_difference(set(ellastname))) <= 4:
                    similar_judges.append(el)
            cur.close()
            return similar_judges
    except Exception as e:
        print(e)
        return 0


async def booknumber_to_name(booknumber):
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
            cur.execute(f"SELECT lastName, firstName FROM competition_judges WHERE bookNumber = {booknumber}")
            jud = cur.fetchone()
            return jud['lastName'] + ' ' +jud['firstName']

    except:
        return 0

async def booknumber_to_name_1(booknumber):
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
            cur.execute(f"SELECT lastName, firstName FROM judges WHERE bookNumber = {booknumber}")
            jud = cur.fetchone()
            return jud['lastName'], jud['firstName']

    except:
        return 0, 0

async def check_clubs_match(list):
    try:
        clubs = {}
        ans = ''
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            for jud in list:
                if len(jud.split()) == 2:
                    k = jud.split()
                    firstname = k[1]
                    lastname = k[0]
                else:
                    k = jud.split()
                    firstname = ' '.join(k[1::])
                    lastname = k[0]

                cur = conn.cursor()
                cur.execute(f"SELECT Club FROM competition_judges WHERE firstName = '{firstname}' AND lastName = '{lastname}'")
                club = cur.fetchone()['Club']
                if club != None:
                    if club not in clubs:
                        clubs[club] = [jud]
                    else:
                        clubs[club].append(jud)
            for club in clubs:
                if len(clubs[club]) > 1:
                    ans = club + ': ' + ', '.join(clubs[club]) + '\n'
            if ans == '':
                return 0
            else:
                return ans

    except Exception as e:
        print(e)
        return 0


async def check_have_tour_date(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            return cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {active_comp}")
    except Exception as e:
        print(e)
        return 0




async def check_category_date(list, user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
        ans = ''
        problem =[]
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
            cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {active_comp}")
            dates = cur.fetchone()
            date1, date2 = dates['date1'], dates['date2']

            for jud in list:
                if len(jud.split()) == 2:
                    k = jud.split()
                    firstname = k[1]
                    lastname = k[0]
                else:
                    k = jud.split()
                    firstname = ' '.join(k[1::])
                    lastname = k[0]

                cur.execute(f"SELECT SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm FROM competition_judges WHERE compId = {active_comp} AND firstName = '{firstname}' AND lastName = '{lastname}'")
                info = cur.fetchone()
                category = info['SPORT_Category']
                SPORT_CategoryDate = info['SPORT_CategoryDate']
                SPORT_CategoryDateConfirm = info['SPORT_CategoryDateConfirm']
                if category == None or SPORT_CategoryDate == None or SPORT_CategoryDateConfirm == None:
                    continue

                if type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) == str:
                    problem.append(jud)
                    continue
                elif type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) != str:
                    CategoryDate = SPORT_CategoryDate
                elif type(SPORT_CategoryDateConfirm) != str and type(SPORT_CategoryDate) == str:
                    CategoryDate = SPORT_CategoryDateConfirm
                else:
                    CategoryDate = max(SPORT_CategoryDateConfirm, SPORT_CategoryDate)

                a = date2 - CategoryDate
                a = a.days
                if category.strip() == 'Первая' or category.strip() == 'Вторая':
                    if a - 365*2 > 0:
                        problem.append(jud)

                elif category.strip() == 'Третья':
                    if a - 365 > 0:
                        problem.append(jud)

                elif category.strip() == 'Всероссийская':
                    if a - 365*4 > 0:
                        problem.append(jud)
            if len(problem) == 0:
                return 0
            else:
                return f"{', '.join(problem)}: на момент окончания турнира категория недействительна"

    except Exception as e:
        print(e)
        return 0



async def check_category_date_for_book_id(book_id, user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
        ans = ''
        problem =[]
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
            cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {active_comp}")
            dates = cur.fetchone()
            date1, date2 = dates['date1'], dates['date2']
            cur.execute(f"SELECT SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm FROM judges WHERE BookNumber = {book_id}")
            info = cur.fetchone()
            category = info['SPORT_Category']
            SPORT_CategoryDate = info['SPORT_CategoryDate']
            SPORT_CategoryDateConfirm = info['SPORT_CategoryDateConfirm']
            if category == None or SPORT_CategoryDate == None or SPORT_CategoryDateConfirm == None:
                return 0

            if type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) == str:
                return 0
            elif type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) != str:
                CategoryDate = SPORT_CategoryDate
            elif type(SPORT_CategoryDateConfirm) != str and type(SPORT_CategoryDate) == str:
                CategoryDate = SPORT_CategoryDateConfirm
            else:
                CategoryDate = max(SPORT_CategoryDateConfirm, SPORT_CategoryDate)

            a = date2 - CategoryDate
            a = a.days
            if category.strip() == 'Первая' or category.strip() == 'Вторая':
                if a - 365 * 2 > 0:
                    return 0

            elif category.strip() == 'Третья':
                if a - 365 > 0:
                    return 0

            elif category.strip() == 'Всероссийская':
                if a - 365 * 4 > 0:
                    return 0
        return 1
    except Exception as e:
        print(e)
        return 0

async def get_tournament_date(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            cur.execute(f"SELECT date2 FROM competition WHERE compId = {active_comp}")
            ans = cur.fetchone()
            return ans['date2']
    except:
        return 0


async def BookNumber_to_name(book_id):
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
            cur.execute(f"SELECT FirstName, LastName FROM judges WHERE BookNumber = {book_id}")
            ans = cur.fetchone()
            return ans['LastName'], ans['FirstName']
    except:
        return 0

async def get_free_judges_for_wrong(user_id, text):
    try:
        ans = []
        active_comp = await general_queries.get_CompId(user_id)
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
            judges_lst = await check_list_judges.get_all_judges(text)
            cur.execute(f"SELECT * FROM competition_judges WHERE is_use = 0 AND compId = {active_comp}")
            free = cur.fetchall()
            if len(free) == 0:
                return 'свободных судей нет'

            free1 = free.copy()
            for jud in free:
                flag = 0
                for jud1 in judges_lst:
                    index = jud1.split()
                    if len(index) == 2:
                        last_name, name = index
                    else:
                        last_name = index[0]
                        name = ' '.join(index[1::])

                    if (jud['firstName'] == name and jud['lastName'] == last_name) or (jud['firstName2'] == name and jud['lastName2'] == last_name):
                        flag = 1

                if flag == 0:
                    ans.append(jud)

            return ans
    except:
        return 0



async def check_cat_for_enter_book_number(user_id, book_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
        book_id = int(book_id)
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
            cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {active_comp}")
            dates = cur.fetchone()
            date1, date2 = dates['date1'], dates['date2']

            cur.execute(
                f"SELECT SPORT_Category, SPORT_CategoryDate, SPORT_CategoryDateConfirm FROM judges WHERE bookNumber = {book_id}")
            info = cur.fetchone()
            print(info)
            print(book_id)
            if info is None:
                return 1

            category = info['SPORT_Category']
            SPORT_CategoryDate = info['SPORT_CategoryDate']
            SPORT_CategoryDateConfirm = info['SPORT_CategoryDateConfirm']
            if category == None or SPORT_CategoryDate == None or SPORT_CategoryDateConfirm == None:
                return 0

            if type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) == str:
                return 0
            elif type(SPORT_CategoryDateConfirm) == str and type(SPORT_CategoryDate) != str:
                CategoryDate = SPORT_CategoryDate
            elif type(SPORT_CategoryDateConfirm) != str and type(SPORT_CategoryDate) == str:
                CategoryDate = SPORT_CategoryDateConfirm
            else:
                CategoryDate = max(SPORT_CategoryDateConfirm, SPORT_CategoryDate)

            a = date2 - CategoryDate
            a = a.days
            if category.strip() == 'Первая' or category.strip() == 'Вторая':
                if a - 365 * 2 > 0:
                    return 0

            elif category.strip() == 'Третья':
                if a - 365 > 0:
                    return 0

            elif category.strip() == 'Всероссийская':
                if a - 365 * 4 > 0:
                    return 0
            return 1

    except Exception as e:
        print(e)
        return 0

async def check_celebrate(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {active_comp}")
            ans = cur.fetchone()
            date1, date2 = ans['date1'], ans['date2']

            cur.execute(f"SELECT lastName, firstName, Birth FROM competition_judges WHERE compId = {active_comp} AND Birth IS NOT NULL")
            ans = cur.fetchall()
            for jud in ans:
                jud['Birth'].year = date1.year
                if type(jud['Birth']) != str:
                    if date1 <= jud['Birth'] <= date2:
                        print(jud)
            return 0
    except Exception as e:
        print(e)
        return 0


async def set_is_use_0(user_id):
    try:
        active_comp = await general_queries.get_CompId(user_id)
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
            cur.execute(f"update competition_judges set is_use = 0 where compId = {active_comp}")
            conn.commit()
    except Exception as e:
        print(e)
        return 0


async def get_comment(user_id):
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
            cur.execute(f"SELECT сomment FROM skatebotusers WHERE tg_id = {user_id}")
            ans = cur.fetchone()
            cur.close()
            return [ans[i] for i in ans][0]
    except Exception as e:
        print(e)
        return 0




async def del_unactive_comp(tg_id, active_comp):
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
            cur.execute(f"SELECT date2 FROM competition WHERE compId = {active_comp}")
            ans = cur.fetchone()
            now = date.today()
            a = now - ans['date2']
            if a.days > 0:
                cur.execute(f"UPDATE skatebotusers set id_active_comp = NULL WHERE tg_id = {tg_id}")
                conn.commit()
            cur.close()
    except Exception as e:
        print(e)
        print('Ошибка выполнения запроса на удаление записи о прошеднем соревновании')
        return 0


async def group_id_to_lin_const(compId, group_num):
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
            cur.execute(f"SELECT judges FROM competition_group WHERE compId = {compId} AND groupNumber = {group_num}")
            ans = cur.fetchone()
            cur.close()
            return ans['judges']
    except Exception as e:
        print(e)
        return 0