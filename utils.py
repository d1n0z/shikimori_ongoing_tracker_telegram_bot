import asyncio
import logging
from datetime import datetime

from aiogram import exceptions
from aiogram.types import URLInputFile
from shikimori_api import Shikimori

from config import bot
from db import Track


def check(id: int | str) -> datetime | str | None:
    api = Shikimori().get_api()
    try:
        anime = api.animes(int(id)).GET()
    except:
        return None
    if anime['next_episode_at'] is not None:
        return datetime.strptime(anime['next_episode_at'], '%Y-%m-%dT%H:%M:%S.%f+03:00')
    return anime['status']


def animename(id: int) -> str | None:
    if t := Track.get_or_none(Track.shikiid == id):
        if t.name is not None:
            return t.name
    api = Shikimori().get_api()
    try:
        anime = api.animes(id).GET()
        return anime['name']
    except:
        pass
    return None


def animephoto(id: int) -> str:
    if t := Track.get_or_none(Track.shikiid == id):
        if t.photo is not None:
            return t.photo
    api = Shikimori().get_api()
    try:
        anime = api.animes(id).GET()
        return f"https://shikimori.one/{anime['image']['original']}"
    except:
        pass
    return 'https://sun9-79.userapi.com/impg/Xdr3JgDTgSW6T2KEZRkNXtOG7_CPgyvbq-cm2w/eMz-HIrIfI0.jpg?size=449x528&quality=95&sign=88ca8e7aee93fd315bf541464021f6df&type=album'  # noqa


async def mass_messaging(user_ids: list, caption: str, photo: str, disable_notification: bool = False) -> int:
    logging.info(f'Start mass messaging to {len(user_ids)} users...')
    count = 0
    for user_id in user_ids:
        count += await send_message_to_users_handler(user_id, caption, photo, disable_notification)
    logging.info(f'Mass messaging completed: {count}/{len(user_ids)} sent')
    return count


async def send_message_to_users_handler(
        user_id: int, caption: str, photo: str, disable_notification: bool = False
) -> bool:
    try:
        await bot.send_photo(user_id, photo=URLInputFile(photo), caption=caption,
                             disable_notification=disable_notification, disable_web_page_preview=True)
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.TelegramNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. "
            f"Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message_to_users_handler(user_id, caption, photo, disable_notification)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    except Exception as e:
        logging.exception(f"Unknown exception:\n{e}")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False
