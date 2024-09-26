import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import chairman_moves.check_list_judges
from queries import get_user_status_query
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import chairmans_kb
from queries import chairman_queries
from queries import scrutineer_queries
from queries import general_queries
from aiogram import types
from chairman_moves import check_list_judges
from handlers import Chairman_comm_handler_02
router = Router()
linsets = {}
problemjudgesset_for_check_lin ={}
current_problem_jud_for_check_lin = {}
bank_for_edit_costyl = {}


#Обработка списка от CHAIRPERSON
@router.message(F.text.lower().contains('линейные судьи'))
async def f2(message: Message):
    user_status = await get_user_status_query.get_user_status(message.from_user.id)
    try:
        linsets.pop(message.from_user.id, None)
        problemjudgesset_for_check_lin.pop(message.from_user.id, None)
        current_problem_jud_for_check_lin.pop(message.from_user.id, None)
        Chairman_comm_handler_02.current_jud_point.pop(message.from_user.id, None)
        Chairman_comm_handler_02.jud_problem_list.pop(message.from_user.id, None)
        Chairman_comm_handler_02.to_index_future.pop(message.from_user.id, None)
        Chairman_comm_handler_02.markup_buttons.pop(message.from_user.id, None)
    except:
        pass


    if user_status == 3:
        if await chairman_queries.check_have_tour_date(message.from_user.id) == 0:
            await message.answer('❌Ошибка. Установите активный турнир')
            return

        #judges_problem - не получилось пробить по competition_judges (в двух полях с именами)
        #judges_problem_db - имя совпало со вторым вариантом, далее в сообщении меняем их имена на имена в judges
        linsets[message.from_user.id] = [message.text, [], [], []]
        judges_problem, judges_problem_db, text_edit = await check_list_judges.get_parse(message.text, message.from_user.id)
        linsets[message.from_user.id][1] = judges_problem
        text = await check_list_judges.transform_linlist(text_edit, judges_problem_db, message.from_user.id)
        linsets[message.from_user.id][0] = text
        #Все пробились в competition_judges
        if judges_problem == []:
            res, msg = await check_list_judges.check_list(text, message.from_user.id)
            linsets[message.from_user.id][3] = msg
            await chairman_queries.set_free_judges(message.from_user.id)
            if res == 1:
                # Перед отправкой сообщения проверяем, совпадает ли выбор турниров у пары и активно ли соревнование
                scrutineer_id = await chairman_queries.get_Scrutineer(message.from_user.id)
                if scrutineer_id == 0:
                    await message.answer('❌Ошибка')
                else:
                    active_compId_chairman = await general_queries.get_CompId(message.from_user.id)
                    active_compId_scrutineer = await general_queries.get_CompId(scrutineer_id)
                    is_active = await general_queries.active_or_not(active_compId_chairman)
                    if is_active == 0:
                        await message.answer('❌Ошибка\nВыбранное соревнование неактивно')
                    elif active_compId_scrutineer == active_compId_chairman:
                        try:
                            if message.from_user.username is None:
                                name = await chairman_queries.get_comment(message.from_user.id)
                            else:
                                name = f'@{message.from_user.username}'
                            await message.bot.send_message(scrutineer_id, f"Сообщение от пользователя {name}")
                            await message.bot.send_message(scrutineer_id, text)
                            await message.answer('✅Информация отправлена РСК')
                        except:
                            print('Бот в бане')
                    else:
                        await message.answer('❌Ошибка\nВыбор турниров не согласуется')
            elif res == 0:
                await chairman_queries.set_free_judges(message.from_user.id)
                await message.answer(text)
                await message.answer(msg, reply_markup=chairmans_kb.list_jud_send_kb)

            elif res == 2:
                await message.answer('❌Ошибка')
        else:
            #Находим замены на тех, кого не получилось пробить
            linsets[message.from_user.id][2] = [await chairman_queries.get_similar_lin_judges(i, message.from_user.id)
                                                for i in linsets[message.from_user.id][1]]


            #Никого и близко нет в бд
            if all(i == [] for i in linsets[message.from_user.id][2]):
                await message.answer(
                    f"🤔{', '.join([i[0] + ' ' + i[1] for i in linsets[message.from_user.id][1]])}: не обнаружены в бд. Пожалуйста загрузите дополнительных судей через /judges или отредактируйте сообщение",
                    reply_markup=chairmans_kb.edit_02_kb)
            else:
                bank_for_edit_costyl[message.from_user.id] = [linsets[message.from_user.id][1], linsets[message.from_user.id][2]]
                text = ''
                for i in range(len(linsets[message.from_user.id][1])):
                    if linsets[message.from_user.id][2][i] != []:
                        text += linsets[message.from_user.id][1][i][0] + ' ' + linsets[message.from_user.id][1][i][
                            1] + ' -> ' + linsets[message.from_user.id][2][i][0]['lastName'] + ' ' + \
                                linsets[message.from_user.id][2][i][0]['firstName'] + ' | ' + str(
                            linsets[message.from_user.id][2][i][0]['City']) + '\n'
                a1 = linsets[message.from_user.id][1]
                a2 = linsets[message.from_user.id][2]
                await message.answer(
                    f"🤔{', '.join([a1[i][0] +  ' ' + a1[i][1] for i in range(len(a1)) if a2[i] != []])}: не обнаружены в бд\n\nВариант замены:\n{text}",
                    reply_markup=chairmans_kb.solve_problem_linjudges_kb)





@router.callback_query(F.data == 'edit_02')
async def edit_linset(callback: types.CallbackQuery):
    await Chairman_comm_handler_02.edit_linlist(callback, callback.message.text)
    return


@router.callback_query(F.data == 'send_with_replace')
async def edit_linset(callback: types.CallbackQuery):
    try:
        text = linsets[callback.from_user.id][0]
        # Заменяем всех по шаблону
        for oldindex in range(len(linsets[callback.from_user.id][1])):
            if linsets[callback.from_user.id][2][oldindex] != []:
                text = text.replace(
                    linsets[callback.from_user.id][1][oldindex][0] + ' ' + linsets[callback.from_user.id][1][oldindex][
                        1],
                    linsets[callback.from_user.id][2][oldindex][0]['lastName'] + ' ' +
                    linsets[callback.from_user.id][2][oldindex][0]['firstName'])

        linsets[callback.from_user.id][0] = text
        if any(i == [] for i in linsets[callback.from_user.id][2]):
            #problem = f"🤔{', '.join([i[0] + ' ' + i[1] for i in linsets[message.from_user.id][1]])}: не обнаружены в бд. Пожалуйста загрузите дополнительных судей через /judges или отредактируйте сообщение"
            a1 = linsets[callback.from_user.id][1]
            a2 = linsets[callback.from_user.id][2]
            problem = f"🤔{', '.join([a1[i][0] +  ' ' + a1[i][1] for i in range(len(a1)) if a2[i] == []])}: не обнаружены в бд. Пожалуйста загрузите дополнительных судей через /judges или отредактируйте сообщение"
            return await Chairman_comm_handler_02.edit_linlist(callback, problem)
        await callback.message.edit_text(text)
        res, msg = await check_list_judges.check_list(text, callback.from_user.id)
        linsets[callback.from_user.id][3] = msg
        await chairman_queries.set_free_judges(callback.from_user.id)
        if res == 1:
            # Перед отправкой сообщения проверяем, совпадает ли выбор турниров у пары и активно ли соревнование
            scrutineer_id = await chairman_queries.get_Scrutineer(callback.from_user.id)
            if scrutineer_id == 0:
                await callback.message.answer('❌Ошибка')
            else:
                active_compId_chairman = await general_queries.get_CompId(callback.from_user.id)
                active_compId_scrutineer = await general_queries.get_CompId(scrutineer_id)
                is_active = await general_queries.active_or_not(active_compId_chairman)
                if is_active == 0:
                    await callback.message.answer('❌Ошибка\nВыбранное соревнование неактивно')
                elif active_compId_scrutineer == active_compId_chairman:
                    try:
                        #await chairman_queries.set_free_judges(callback.from_user.id)
                        if callback.from_user.username is None:
                            name = await chairman_queries.get_comment(callback.from_user.id)
                        else:
                            name = f'@{callback.from_user.username}'
                        await callback.message.bot.send_message(scrutineer_id,
                                                       f"Сообщение от пользователя {name}")
                        await callback.message.bot.send_message(scrutineer_id, text)
                        await callback.message.answer('✅Информация отправлена РСК')
                    except:
                        print('Бот в бане')
                else:
                    await callback.message.answer('❌Ошибка\nВыбор турниров не согласуется')
        elif res == 0:
            await callback.message.answer(msg, reply_markup=chairmans_kb.list_jud_send_kb)

        elif res == 2:
            await callback.message.answer('❌Ошибка')

    except Exception as e:
        print(e)
        await callback.message.answer('❌Ошибка. Пожалуйста отправьте список еще раз')



#Редактировать бригадный список
@router.callback_query(F.data == 'to_edit_linlist')
async def edit_linset(callback: types.CallbackQuery):
    try:
        problemJudges = []
        if [] in linsets[callback.from_user.id][2]:
            bank_for_edit_costyl[callback.from_user.id][0] = linsets[callback.from_user.id][1]
            bank_for_edit_costyl[callback.from_user.id][1] = linsets[callback.from_user.id][2]

        linsets[callback.from_user.id][1] = [linsets[callback.from_user.id][1][i] for i in range(len(linsets[callback.from_user.id][1])) if linsets[callback.from_user.id][2][i] != []]
        linsets[callback.from_user.id][2] = [i for i in linsets[callback.from_user.id][2] if i != []]
        problemJudges = linsets[callback.from_user.id][1]

        #Отредактировали тех, кого изначально не получилось пробить
        if problemJudges == []:
            linsets[callback.from_user.id][1] = bank_for_edit_costyl[callback.from_user.id][0]
            linsets[callback.from_user.id][2] = bank_for_edit_costyl[callback.from_user.id][1]
            if any(i == [] for i in linsets[callback.from_user.id][2]):
                # problem = f"🤔{', '.join([i[0] + ' ' + i[1] for i in linsets[message.from_user.id][1]])}: не обнаружены в бд. Пожалуйста загрузите дополнительных судей через /judges или отредактируйте сообщение"
                a1 = linsets[callback.from_user.id][1]
                a2 = linsets[callback.from_user.id][2]
                problem = f"🤔{', '.join([a1[i][0] + ' ' + a1[i][1] for i in range(len(a1)) if a2[i] == []])}: не обнаружены в бд. Пожалуйста загрузите дополнительных судей через /judges или отредактируйте сообщение"
                return await Chairman_comm_handler_02.edit_linlist(callback, problem)


            res, msg = await check_list_judges.check_list(linsets[callback.from_user.id][0], callback.from_user.id)
            await chairman_queries.set_free_judges(callback.from_user.id)
            if res == 1:
                # Перед отправкой сообщения проверяем, совпадает ли выбор турниров у пары и активно ли соревнование
                scrutineer_id = await chairman_queries.get_Scrutineer(callback.from_user.id)
                if scrutineer_id == 0:
                    await callback.message.answer('❌Ошибка')
                else:
                    active_compId_chairman = await general_queries.get_CompId(callback.from_user.id)
                    active_compId_scrutineer = await general_queries.get_CompId(scrutineer_id)
                    is_active = await general_queries.active_or_not(active_compId_chairman)
                    if is_active == 0:
                        await callback.message.answer('❌Ошибка\nВыбранное соревнование неактивно')
                    elif active_compId_scrutineer == active_compId_chairman:
                        try:
                            #await chairman_queries.set_free_judges(callback.from_user.id)
                            if callback.from_user.username is None:
                                name = await chairman_queries.get_comment(callback.from_user.id)
                            else:
                                name = f'@{callback.from_user.username}'
                            await callback.message.bot.send_message(scrutineer_id,
                                                           f"Сообщение от пользователя {name}")
                            await callback.message.bot.send_message(scrutineer_id, linsets[callback.from_user.id][0])
                            await callback.message.delete()
                            await callback.message.answer(linsets[callback.from_user.id][0])
                            await callback.message.answer('✅Информация отправлена РСК')
                        except:
                            print('Бот в бане')
                    else:
                        await callback.message.answer('❌Ошибка\nВыбор турниров не согласуется')
            elif res == 0:
                await callback.message.edit_text(linsets[callback.from_user.id][0])
                linsets[callback.from_user.id][3] = msg
                await callback.message.answer(msg, reply_markup=chairmans_kb.list_jud_send_kb)

            elif res == 2:
                await callback.message.answer('❌Ошибка')
            return

        #Остались проблемные друзья
        current_problem_jud_for_check_lin[callback.from_user.id] = linsets[callback.from_user.id][1].pop(0)
        replace = linsets[callback.from_user.id][2].pop(0)
        list_comp_buttons = []
        for jud in replace:
            list_comp_buttons.append([InlineKeyboardButton(text=jud['lastName'] + ' ' + jud['firstName'] + '|' + str(jud['City']),
                                                           callback_data=f"replin_{jud['bookNumber']}")])

        list_comp_buttons.append([InlineKeyboardButton(text='Отменить редактирование и отправку', callback_data='cancel_edit_linset')])
        markup = InlineKeyboardMarkup(inline_keyboard=list_comp_buttons)
        await callback.message.edit_text(f'{current_problem_jud_for_check_lin[callback.from_user.id][0]} {current_problem_jud_for_check_lin[callback.from_user.id][1]}\nВыберите замену:', reply_markup=markup)
    except Exception as e:
        print(e)
        await callback.message.answer('Во время редактирования возникла ошибка. Пожайлуста отправьте список еще раз')


@router.callback_query(F.data.startswith('replin_'))
async def cmd_start(call: types.CallbackQuery):
    try:
        BookNumber = int(call.data.replace('replin_', ''))
        name = await chairman_queries.booknumber_to_name(BookNumber)
        old = current_problem_jud_for_check_lin[call.from_user.id][0] + ' ' + current_problem_jud_for_check_lin[call.from_user.id][1]
        linsets[call.from_user.id][0] = linsets[call.from_user.id][0].replace(old, name)
        await edit_linset(call)
    except:
        await call.message.answer('Во время редактирования возникла ошибка. Пожалуйста отправьте список еще раз')


@router.callback_query(F.data == 'cancel_edit_linset')
async def cmd_start(call: types.CallbackQuery):
    try:
        linsets.pop(call.from_user.id, None)
        problemjudgesset_for_check_lin.pop(call.from_user.id, None)
        current_problem_jud_for_check_lin.pop(call.from_user.id, None)
        Chairman_comm_handler_02.current_jud_point.pop(call.from_user.id, None)
        Chairman_comm_handler_02.jud_problem_list.pop(call.from_user.id, None)
        Chairman_comm_handler_02.to_index_future.pop(call.from_user.id, None)
        Chairman_comm_handler_02.markup_buttons.pop(call.from_user.id, None)
        bank_for_edit_costyl.pop(call.from_user.id, None)
    except:
        pass
    await call.message.delete()
    await call.message.answer('Действие обработано')


#Подтверждаем отправку списка линейных
@router.callback_query(F.data == 'send_list_anyway')
async def f4(callback: types.CallbackQuery):
    try:
        text = linsets[callback.from_user.id][0]
    except:
        text = 0

    if text != 0:
        scrutineer_id = await chairman_queries.get_Scrutineer(callback.from_user.id)
        if scrutineer_id == 0:
            await callback.message.answer('❌Ошибка')
        else:
            active_compId_chairman = await general_queries.get_CompId(callback.from_user.id)
            active_compId_scrutineer = await general_queries.get_CompId(scrutineer_id)
            is_active = await general_queries.active_or_not(active_compId_chairman)
            if is_active == 0:
                await callback.message.answer('❌Ошибка\nВыбранное соревнование неактивно')

            elif active_compId_scrutineer == active_compId_chairman:
                try:
                    #r = await chairman_queries.set_free_judges(callback.from_user.id)
                    r = 1
                    if r == 1:
                        if callback.from_user.username is None:
                            name = await chairman_queries.get_comment(callback.from_user.id)
                        else:
                            name = f'@{callback.from_user.username}'
                        await callback.message.bot.send_message(scrutineer_id, f"Сообщение от пользователя {name}")
                        await callback.message.bot.send_message(scrutineer_id, text)
                        await callback.message.bot.send_message(scrutineer_id, linsets[callback.from_user.id][3])
                        await callback.message.delete()
                        await callback.message.answer('✅Информация отправлена РСК')
                    else:
                        await callback.message.answer('❌Ошибка. Пожалуйста отправьте список еще раз')
                except Exception as e:
                    print(e)
                    await callback.message.answer('❌Ошибка. Пожалуйста отправьте список еще раз')
            else:
                await callback.message.answer('❌Ошибка\nВыбор турниров не согласуется')

    else:
        await callback.message.answer('❌Ошибка, отправьте список еще раз')


#Показать свободных судей
@router.callback_query(F.data == 'show_free_judges')
async def f4(callback: types.CallbackQuery):
    try:
        a = await chairman_queries.get_free_judges(callback.from_user.id)
        if a == 0:
            await callback.message.answer('❌Ошибка, отправьте список еще раз')
        else:
            await callback.message.edit_text(callback.message.text + f'\n\n<b>Свободные судьи:</b> {a}', reply_markup=chairmans_kb.list_jud_send_kb, parse_mode='html')
    except Exception as e:
        print(e)
        await callback.message.answer('❌Ошибка, отправьте список еще раз')


#Обработка сообщений между scrutineer и chairman
@router.message()
async def f3(message: Message):
    user_status = await get_user_status_query.get_user_status(message.from_user.id)
    if user_status == 3:
        scrutineer_id = await chairman_queries.get_Scrutineer(message.from_user.id)
        if scrutineer_id == 0:
            await message.answer('❌Ошибка')
        else:
            active_compId_chairman = await general_queries.get_CompId(message.from_user.id)
            active_compId_scrutineer = await general_queries.get_CompId(scrutineer_id)
            is_active = await general_queries.active_or_not(active_compId_chairman)
            if is_active == 0:
                await message.answer('❌Ошибка\nВыбранное соревнование неактивно')
            elif active_compId_scrutineer == active_compId_chairman:
                try:
                    await message.bot.forward_message(scrutineer_id, message.chat.id, message.message_id)
                except:
                    print('Бот в бане')
            else:
                await message.answer('❌Ошибка\nВыбор турниров не согласуется')

    if user_status == 2:
        chairman_id = await scrutineer_queries.get_Chairman(message.from_user.id)
        if chairman_id == 0:
            await message.answer('❌Ошибка')
        else:
            active_compId_scrutineer = await general_queries.get_CompId(message.from_user.id)
            active_compId_chairman = await general_queries.get_CompId(chairman_id)
            is_active = await general_queries.active_or_not(active_compId_scrutineer)
            if is_active == 0:
                await message.answer('❌Ошибка\nВыбранное соревнование неактивно')
            elif active_compId_scrutineer == active_compId_chairman:
                try:
                    await message.bot.forward_message(chairman_id, message.chat.id, message.message_id)
                except:
                    print('Бот в бане')
            else:
                await message.answer('❌Ошибка\nВыбор турниров не согласуется')
