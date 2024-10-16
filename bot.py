import re
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile

import keyboard
import states
from config import bot
from db import Track, UsersTrack
from utils import check, animename, animephoto

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        text='Привет. Это бесплатный сервис по трекингу онгоингов аниме. Чтобы начать, напиши /settings.'
    )


@dp.callback_query(keyboard.Callback.filter(F.type == 'settings'))
async def settings(message: Message, state: FSMContext) -> None:
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await bot.send_message(chat_id=message.from_user.id, text='Что смотрим?',
                                 reply_markup=keyboard.settings())
    await state.clear()
    await state.update_data(msg=msg)


@dp.message(Command('settings'))
async def settings(message: Message, state: FSMContext) -> None:
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await message.answer('Что смотрим?', reply_markup=keyboard.settings())
    await state.clear()
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'add_ongoing'))
async def add_ongoing(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text='Чтобы добавить онгоинг в список отслеживания, '
             'отправь на него ссылку с <a href="https://shikimori.one/animes">Shikimori</a>:',
        reply_markup=keyboard.back())
    await state.set_state(states.Ongoing.add.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'del_ongoing'))
async def del_ongoing(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text='Чтобы удалить онгоинг из списка отслеживания, '
             'отправь на него ссылку с <a href="https://shikimori.one/animes">Shikimori</a>:',
        reply_markup=keyboard.back())
    await state.set_state(states.Ongoing.delete.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'my_ongoings'))
async def my_ongoings(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    ongoings = UsersTrack.select().where(UsersTrack.uid == query.from_user.id)
    if len(ongoings) == 0:
        text = 'Нет отслеживаемых онгоингов.'
    else:
        text = 'Список отслеживаемых онгоингов:\n'
        for k, i in enumerate(ongoings):
            i: UsersTrack
            nextep = datetime.fromtimestamp(Track.get(Track.shikiid == i.shikiid).nextep).strftime("%d.%m в %H:00")
            text += (f'[{k + 1}]. id{i.shikiid} | '
                     f'<a href="https://shikimori.one/animes/{i.shikiid}">{animename(i.shikiid)}</a> | {nextep}\n')
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text=text,
        reply_markup=keyboard.back())
    await state.update_data(msg=msg)


@dp.message()
async def statehandler(message: Message, state: FSMContext):
    curr_state = await state.get_state()
    if curr_state is None:
        return

    msg: Message = (await state.get_data())['msg']
    await message.delete()
    await msg.delete()

    if curr_state == states.Ongoing.add.state:
        res = re.search(r'shikimori\.(?:one|net|me)/animes/*', message.text)
        id = message.text
        if res is not None:
            id = message.text[res.end():].split('-')[0]
        checked = check(id)
        if not id.isdigit() or checked is None:
            msg = await bot.send_message(chat_id=message.from_user.id, text='⚠️ Неверная ссылка.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        if checked == 'released':
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Данное аниме уже закончилось. Новых серий больше не будет. :c',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        if checked == 'anons':
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Данное аниме анонсировано. Дата выхода новых серий неизвестна.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        if isinstance(checked, str):
            msg = await bot.send_message(
                chat_id=message.from_user.id,
                text='⚠️ Неизвестный статус аниме. Пожалуйста, свяжитесь со <a href="https://t.me/d1n0_zvr">мной</a>.',
                reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        id = int(id)
        track: Track = Track.get_or_create(shikiid=id)[0]
        track.nextep = checked.timestamp()
        track.name = animename(id)
        track.photo = animephoto(id)
        track.save()
        UsersTrack.get_or_create(uid=message.from_user.id, shikiid=track.shikiid)
        msg = await bot.send_photo(
            chat_id=message.from_user.id,
            photo=URLInputFile(track.photo),
            caption=f'✅ Теперь бот будет отправлять вам уведомления о выходе новых серий "{track.name}".',
            reply_markup=keyboard.back()
        )
    elif curr_state == states.Ongoing.delete.state:
        res = re.search(r'shikimori\.(?:one|net|me)/animes/*', message.text)
        id = message.text
        if res is not None:
            id = message.text[res.end():].split('-')[0]
        if not id.isdigit():
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Неверная ссылка.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        id = int(id)
        ut: UsersTrack = UsersTrack.get_or_none(uid=message.from_user.id, shikiid=id)
        if ut is None:
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Данного аниме нет в списке отслеживаемых онгоингов.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        track = Track.get(Track.shikiid == ut.shikiid)
        name = track.name
        photo = track.photo
        UsersTrack.delete().where(UsersTrack.shikiid == ut.shikiid, UsersTrack.uid == ut.uid).execute()
        if UsersTrack.select().where(UsersTrack.shikiid == ut.shikiid).count() == 0:
            Track.delete().where(Track.shikiid == ut.shikiid).execute()
        msg = await bot.send_photo(
            chat_id=message.from_user.id,
            photo=URLInputFile(photo),
            caption=f'✅ Отслеживание аниме "{name}" отключено.',
            reply_markup=keyboard.back()
        )
    await state.clear()
    await state.update_data(msg=msg)
