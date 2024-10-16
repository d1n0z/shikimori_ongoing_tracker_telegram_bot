import asyncio
import logging
import time
import traceback
from datetime import datetime

import aiocron

from db import Track, UsersTrack
from utils import mass_messaging, check, animephoto


async def checker():
    try:
        for i in Track.select().where(Track.nextep < time.time()):
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
                i.nextep = checked.timestamp()
                i.save()
                text += f'Следующая серия выйдет {datetime.fromtimestamp(i.nextep).strftime("%d.%m в %H:00")}'
            await mass_messaging(
                [y.uid for y in UsersTrack.select().where(UsersTrack.shikiid == i.shikiid)], text, i.photo)
            await asyncio.sleep(1)
    except:
        logging.exception(f'Exception excepted!\n{traceback.format_exc()}')


async def run():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    aiocron.crontab('13 */1 * * *', func=checker, loop=loop)
