from itertools import groupby

from shikimori.client import Shikimori
from shikimori.types.auth import AccessTokenData
from shikimori.types.user import Rate

from config import SHIKI_CLIENT_ID, SHIKI_CLIENT_SECRET
from db import UsersShikimoriTokens


def getClient() -> Shikimori:
    return Shikimori(user_agent="TrackBot", client_id=SHIKI_CLIENT_ID, client_secret=SHIKI_CLIENT_SECRET)


async def getAccessToken(client: Shikimori, uid: int, code: str = None) -> AccessTokenData:
    ust: UsersShikimoriTokens = UsersShikimoriTokens.get_or_none(UsersShikimoriTokens.uid == uid)
    if ust is not None:
        return AccessTokenData(access_token=ust.access, token_type='Bearer', expires_in=86400,
                               refresh_token=ust.refresh, scope='user_rates', created_at=ust.expires_at - 86400)
    if code is None:
        raise Exception("UST doesn't exist and code is None")
    token = await client.auth.get_access_token(code)
    if not isinstance(token, AccessTokenData):
        raise token
    ust: UsersShikimoriTokens = UsersShikimoriTokens.get_or_create(uid=uid)[0]
    ust.access = token.access_token
    ust.refresh = token.refresh_token
    ust.expires_at = token.created_at + token.expires_in
    ust.save()
    return token


async def refreshToken(client: Shikimori, uid: int, client_logged: bool = False) -> None:
    ust: UsersShikimoriTokens = UsersShikimoriTokens.get(UsersShikimoriTokens.uid == uid)
    if not client_logged:
        client.set_token(ust.access)
    token = await client.auth.refresh(ust.refresh)
    ust.access = token.access_token
    ust.refresh = token.refresh_token
    ust.expires_at = token.created_at + token.expires_in
    ust.save()
    return


async def getOngoingList(client: Shikimori) -> list[Rate]:
    ol = []
    page = 1
    id = (await client.user.whoami()).id
    animerates = await client.user.animeRates(id=id, limit=100, page=page)
    ol.extend(animerates)
    while True:
        page += 1
        try:
            animerates = await client.user.animeRates(id=id, limit=100, page=page)
        except:
            break
        ol.extend(animerates)
    return [k for k, _ in groupby(ol) if k.anime.status == 'ongoing' and k.status != 'dropped']
