import asyncio
import logging
import time
import traceback
from datetime import datetime

import aiocron

import shikimori_utils
import keyboard
from db import Track, UsersTrack, NotUpdatedTrack, UsersShikimoriTokens
from utils import check, animephoto, mass_messaging, animename, animeepisodes


async def checker():
    try:
        await asyncio.sleep(10)
        updating = [i.shikiid for i in NotUpdatedTrack.select().where(NotUpdatedTrack.nextupdate.is_null(False))]
        for i in Track.select().where(Track.nextep < time.time(), Track.shikiid.not_in(updating)):
            i: Track
            if i.name is None:
                continue
            if i.photo is None:
                i.photo = animephoto(i.shikiid)
                i.save()
            episodes = animeepisodes(i.shikiid)
            epprogress = f'{episodes[0] + 1}/{episodes[1]}' if episodes else 'новая'
            text = f'Вышла {epprogress} серия аниме <a href="https://shikimori.one/animes/{i.shikiid}">{i.name}</a>!\n'

            checked = check(i.shikiid)
            if isinstance(checked, str | None):
                if episodes and (episodes[0] + 1) >= episodes[1]:
                    text += 'Это последняя серия. Отслеживание аниме автоматически отключено'
                elif checked is None:
                    i.delete_instance()
            else:
                checked = int(checked.timestamp())
                if i.nextep != checked:
                    i.nextep = checked
                    i.save()
                else:
                    t: NotUpdatedTrack = NotUpdatedTrack.get_or_create(shikiid=i.shikiid)[0]
                    t.nextupdate = datetime.now().timestamp() + 300
                    t.save()

            await mass_messaging([y.uid for y in UsersTrack.select().where(UsersTrack.shikiid == i.shikiid)],
                                 text, i, checked, keyboard.support())
            await asyncio.sleep(1)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def updater():
    try:
        for i in NotUpdatedTrack.select().where(NotUpdatedTrack.nextupdate < time.time()):
            i: NotUpdatedTrack
            t: Track = Track.get_or_none(Track.shikiid == i.shikiid)
            if t is None:
                i.delete_instance()
                continue
            checked = check(i.shikiid)
            if isinstance(checked, datetime):
                if t.nextep == int(checked.timestamp()):
                    i.nextupdate += 300
                    i.save()
                else:
                    t.nextep = checked.timestamp()
                    t.save()
                    i.delete_instance()
            else:
                UsersTrack.delete().where(UsersTrack.shikiid == i.shikiid).execute()
                i.delete_instance()
                t.delete_instance()
            await asyncio.sleep(1)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def tokenrefresher():
    try:
        for i in UsersShikimoriTokens.select().where(UsersShikimoriTokens.expires_at < time.time() + 10800):
            i: UsersShikimoriTokens
            await shikimori_utils.refreshToken(client=shikimori_utils.getClient(), uid=i.uid)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def resyncer():
    try:
        for i in UsersShikimoriTokens.select().where(UsersShikimoriTokens.access.is_null(False),
                                                     UsersShikimoriTokens.expires_at < time.time()):
            i: UsersShikimoriTokens
            client = shikimori_utils.getClient()
            client.set_token(i.access)
            ol = await shikimori_utils.getOngoingList(client)
            for y in ol:
                y = y.anime
                track: Track = Track.get_or_create(shikiid=y.id)[0]
                track.nextep = check(y.id).timestamp()
                track.name = animename(y.id)
                track.photo = animephoto(y.id)
                track.save()
                UsersTrack.get_or_create(uid=i.uid, shikiid=track.shikiid)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def run():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    aiocron.crontab('0 */1 * * *', func=checker, loop=loop)
    aiocron.crontab('30 */1 * * *', func=resyncer, loop=loop)
    aiocron.crontab('*/1 * * * *', func=updater, loop=loop)
    aiocron.crontab('*/1 * * * *', func=tokenrefresher, loop=loop)
