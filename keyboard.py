from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Callback(CallbackData, prefix='cb'):
    type: str


def settings() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Добавить онгоинг', callback_data=Callback(type='add_ongoing').pack()))
    builder.row(InlineKeyboardButton(text='Мои онгоинги', callback_data=Callback(type='my_ongoings').pack()))
    builder.row(InlineKeyboardButton(text='Убрать онгоинг', callback_data=Callback(type='del_ongoing').pack()))

    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Назад', callback_data=Callback(type='settings').pack()))

    return builder.as_markup()
