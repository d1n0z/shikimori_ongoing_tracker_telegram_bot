import asyncio
import logging
import time
import traceback
from datetime import datetime

import aiocron

from db import Track, UsersTrack, NotUpdatedTrack
from utils import mass_messaging, check, animephoto


async def checker():
    try:
        await asyncio.sleep(10)
        updating = [i.shikiid for i in NotUpdatedTrack.select()]
        for i in Track.select().where(Track.nextep < time.time(), Track.shikiid.not_in(updating)):
            i: Track
            if i.name is None:
                continue
            if i.photo is None:
                i.photo = animephoto(i.shikiid)
                i.save()
            text = f'Вышла новая серия аниме <a href="https://shikimori.one/animes/{i.shikiid}">{i.name}</a>!\n'
            checked = check(i.shikiid)
            if isinstance(checked, str):
                if checked == 'released':
                    text += 'Это последняя серия. Отслеживание аниме автоматически отключено'
                else:
                    text += f'Статус аниме изменился на {checked}. Отслеживание аниме автоматически отключено'
            elif checked is None:
                i.delete_instance()
            else:
                if i.nextep == int(checked.timestamp()):
                    t: NotUpdatedTrack = NotUpdatedTrack.get_or_create(shikiid=i.shikiid)
                    t.nextupdate = datetime.now().timestamp() + 300
                    t.save()
                    i.nextep += 604800
                    text += f'Следующая серия ожидается {datetime.fromtimestamp(i.nextep).strftime("%d.%m в %H:%M")}'
                else:
                    i.nextep = checked.timestamp()
                    text += f'Следующая серия выйдет {datetime.fromtimestamp(i.nextep).strftime("%d.%m в %H:%M")}'
                i.save()
            await mass_messaging(
                [y.uid for y in UsersTrack.select().where(UsersTrack.shikiid == i.shikiid)], text, i.photo)
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
            if not isinstance(checked, datetime) or t.nextep == int(checked.timestamp()):
                i.nextupdate += 300
                i.save()
                continue
            t.nextep = checked.timestamp()
            t.save()
            i.delete_instance()
            await asyncio.sleep(1)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def run():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    aiocron.crontab('0 */1 * * *', func=checker, loop=loop)
    aiocron.crontab('*/1 * * * *', func=updater, loop=loop)
