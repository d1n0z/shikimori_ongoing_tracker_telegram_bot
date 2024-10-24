from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import DONATION_URL


class Callback(CallbackData, prefix='cb'):
    type: str


def settings() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Добавить онгоинг', callback_data=Callback(type='add_ongoing').pack()))
    builder.row(InlineKeyboardButton(text='Мои онгоинги', callback_data=Callback(type='my_ongoings').pack()))
    builder.row(InlineKeyboardButton(text='Убрать онгоинг', callback_data=Callback(type='del_ongoing').pack()))
    builder.row(InlineKeyboardButton(text='Синхронизация', callback_data=Callback(type='sync').pack()))
    builder.row(InlineKeyboardButton(text='Мой часовой пояс', callback_data=Callback(type='my_timezone').pack()))
    builder.row(InlineKeyboardButton(text='Поддержать автора', url=DONATION_URL))

    return builder.as_markup()


def support() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Поддержать автора', url=DONATION_URL))
    return builder.as_markup()


def back(don: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))
    if don:
        builder.row(InlineKeyboardButton(text='Поддержать автора', url=DONATION_URL))
    return builder.as_markup()


def change_timezone() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))
    builder.row(InlineKeyboardButton(text='Установить', callback_data=Callback(type='set_timezone').pack()))
    return builder.as_markup()


def sync() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))
    builder.row(InlineKeyboardButton(text='Shikimori', callback_data=Callback(type='sync_shikimori').pack()))
    # builder.row(InlineKeyboardButton(text='MyAnimeList', callback_data=Callback(type='sync_mal').pack()))
    builder.row(InlineKeyboardButton(text='Поддержать автора', url=DONATION_URL))
    return builder.as_markup()


def sync_control(platform: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))
    builder.row(InlineKeyboardButton(text='Убрать', callback_data=Callback(type=f'unsync_{platform}').pack()))
    builder.row(InlineKeyboardButton(text='Синхронизировать', callback_data=Callback(type=f'resync_{platform}').pack()))
    builder.row(InlineKeyboardButton(text='Поддержать автора', url=DONATION_URL))
    return builder.as_markup()


def sync_platform(url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='OAuth', url=url))
    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))
    return builder.as_markup()
