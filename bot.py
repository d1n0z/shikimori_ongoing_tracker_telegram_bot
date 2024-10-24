import re

import pytz
from timezonefinder import TimezoneFinder
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile

import keyboard
import shikimori_utils
import states
from config import bot, SHIKI_OAUTH_URL
from db import Track, UsersTrack, UsersTimezone, UsersShikimoriTokens
from utils import check, animename, animephoto, getdate

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        text='Привет. Это бесплатный сервис по трекингу онгоингов аниме. Чтобы начать, напиши /settings.',
        reply_markup=keyboard.support()
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
        text='Чтобы добавить онгоинг в список отслеживания, перейди в раздел "Синхронизация" или '
             'отправь его ссылку либо ID с <a href="https://shikimori.one/animes">Shikimori</a>:',
        reply_markup=keyboard.back(), disable_web_page_preview=True)
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
             'отправь его ссылку либо ID с <a href="https://shikimori.one/animes">Shikimori</a>:',
        reply_markup=keyboard.back(), disable_web_page_preview=True)
    await state.set_state(states.Ongoing.delete.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'set_timezone'))
async def set_timezone(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text='Чтобы установить новый часовой пояс, отправьте геолокацию или введите один из '
             '<a href="https://gist.githubusercontent.com/JellyWX/913dfc8b63d45192ad6cb54c829324ee/raw/'
             '3de52488ba2f24383d943681ec428dfa4f306e2c/PYTZ%2520Timezone%2520List">списка(pytz)</a>:',
        reply_markup=keyboard.back(), disable_web_page_preview=True)
    await state.set_state(states.Timezone.set.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'sync_shikimori'))
async def sync_shikimori(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    if not UsersShikimoriTokens.get_or_none(UsersShikimoriTokens.uid == query.from_user.id):
        msg = await bot.send_message(
            chat_id=query.from_user.id,
            text=f'Чтобы добавить все онгоинги из твоего списка аниме, перейди по <a href="{SHIKI_OAUTH_URL}">'
                 f'ссылке</a> и отправь код авторизации:',
            reply_markup=keyboard.sync_platform(SHIKI_OAUTH_URL), disable_web_page_preview=True)
    else:
        msg = await bot.send_message(
            chat_id=query.from_user.id,
            text='Управление синхронизацией с Shikimori',
            reply_markup=keyboard.sync_control('shikimori'), disable_web_page_preview=True)
    await state.set_state(states.Sync.shikimori.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'resync_shikimori'))
async def resync_shikimori(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    token = await shikimori_utils.getAccessToken(client=shikimori_utils.getClient(), uid=query.from_user.id)
    client = shikimori_utils.getClient()
    client.set_token(token.access_token)
    ol = await shikimori_utils.getOngoingList(client)
    for i in ol:
        i = i.anime
        track: Track = Track.get_or_create(shikiid=i.id)[0]
        track.nextep = check(i.id).timestamp()
        track.name = animename(i.id)
        track.photo = animephoto(i.id)
        track.save()
        UsersTrack.get_or_create(uid=query.from_user.id, shikiid=track.shikiid)
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text='💚 Список был синхронизирован!',
        reply_markup=keyboard.back(don=True), disable_web_page_preview=True)
    await state.set_state(states.Sync.shikimori.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'unsync_shikimori'))
async def unsync_shikimori(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    UsersShikimoriTokens.delete().where(UsersShikimoriTokens.uid == query.from_user.id).execute()
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text='💚 Shikimori был отвязан от вашей учётной записи.',
        reply_markup=keyboard.back(don=True), disable_web_page_preview=True)
    await state.set_state(states.Sync.shikimori.state)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'my_timezone'))
async def my_timezone(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    tz = UsersTimezone.get_or_create(uid=query.from_user.id)[0].timezone
    msg = await bot.send_message(
        chat_id=query.from_user.id,
        text=f'Текущий часовой пояс: {tz}.',
        reply_markup=keyboard.change_timezone(), disable_web_page_preview=True)
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
        utz = UsersTimezone.get_or_create(uid=query.from_user.id)[0].timezone
        text = 'Список отслеживаемых онгоингов:\n'
        ongoings = Track.select().where(Track.shikiid << [i.shikiid for i in ongoings]).order_by(Track.nextep.asc())
        for k, i in enumerate(ongoings):
            i: Track
            nextep = getdate(Track.get(Track.shikiid == i.shikiid).nextep, utz)
            text += (f'[{k + 1}]. id{i.shikiid} | '
                     f'<a href="https://shikimori.one/animes/{i.shikiid}">{animename(i.shikiid)}</a> | {nextep}\n')
    msg = await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=keyboard.back(don=True),
                                 disable_web_page_preview=True)
    await state.update_data(msg=msg)


@dp.callback_query(keyboard.Callback.filter(F.type == 'sync'))
async def sync(query: CallbackQuery, state: FSMContext):
    try:
        msg: Message = (await state.get_data())['msg']
        await msg.delete()
    except:
        pass
    msg = await bot.send_message(chat_id=query.from_user.id, text='Здесь ты можешь настроить синхронизацию с сервисами',
                                 reply_markup=keyboard.sync(), disable_web_page_preview=True)
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
                reply_markup=keyboard.back(), disable_web_page_preview=True)
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
            caption=f'💚 Теперь бот будет отправлять вам уведомления о выходе новых серий "{track.name}".',
            reply_markup=keyboard.back(don=True)
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
            caption=f'💚 Отслеживание аниме "{name}" отключено.',
            reply_markup=keyboard.back(don=True),
        )
    elif curr_state == states.Timezone.set.state:
        try:
            if message.location is None:
                tz = pytz.timezone(message.text)
            else:
                tz = pytz.timezone(TimezoneFinder().timezone_at(lng=message.location.longitude,
                                                                lat=message.location.latitude))
        except pytz.exceptions.UnknownTimeZoneError:
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Неверный часовой пояс.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        utz: UsersTimezone = UsersTimezone.get_or_create(uid=message.from_user.id)[0]
        utz.timezone = tz.zone
        utz.save()
        msg = await bot.send_message(
            chat_id=message.from_user.id,
            text=f'💚 Часовой пояс успешно изменён на {tz.zone}!',
            reply_markup=keyboard.back(don=True),
        )
    elif curr_state == states.Sync.shikimori.state:
        try:
            token = await shikimori_utils.getAccessToken(client=shikimori_utils.getClient(), code=message.text,
                                                         uid=message.from_user.id)
        except:
            msg = await bot.send_message(chat_id=message.from_user.id,
                                         text='⚠️ Неверный код.',
                                         reply_markup=keyboard.back())
            await state.update_data(msg=msg)
            return
        client = shikimori_utils.getClient()
        client.set_token(token.access_token)
        ol = await shikimori_utils.getOngoingList(client)
        for i in ol:
            i = i.anime
            track: Track = Track.get_or_create(shikiid=i.id)[0]
            track.nextep = check(i.id).timestamp()
            track.name = animename(i.id)
            track.photo = animephoto(i.id)
            track.save()
            UsersTrack.get_or_create(uid=message.from_user.id, shikiid=track.shikiid)
        msg = await bot.send_message(
            chat_id=message.from_user.id,
            text=f'💚 Успешная синхронизация с Shikimori!\nОнгоинги из списка были добавлены в список отслеживания.',
            reply_markup=keyboard.back(don=True),
        )
    await state.clear()
    await state.update_data(msg=msg)
