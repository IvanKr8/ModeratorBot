import re
from typing import Any
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Bot
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest


def format_time(time_string: str) -> str:
    match_ = re.match(r"(\d+)([a-z]*)", time_string.lower().strip())
    if match_:
        value, unit = int(match_.group(1)), match_.group(2)
        if not unit:  # default to minutes if no unit is provided
            unit = "m"
        if unit == "m":
            if value == 1:
                return f"{value} минуту"
            elif 2 <= value <= 4:
                return f"{value} минуты"
            else:
                return f"{value} минут"
        elif unit == "h":
            if value == 1:
                return f"{value} час"
            elif 2 <= value <= 4:
                return f"{value} часа"
            else:
                return f"{value} часов"
        elif unit == "d":
            if value == 1:
                return f"{value} день"
            elif 2 <= value <= 4:
                return f"{value} дня"
            else:
                return f"{value} дней"
        elif unit == "w":
            if value == 1:
                return f"{value} неделю"
            elif 2 <= value <= 4:
                return f"{value} недели"
            else:
                return f"{value} недель"
    return time_string


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None
    match_ = re.match(r"(\d+)([a-z]*)", time_string.lower().strip())
    current_datetime = datetime.now()
    print(f"s: {current_datetime}")

    if match_:
        value, unit = int(match_.group(1)), match_.group(2)

        match unit:
            case "m": time_delta = timedelta(minutes=value)
            case "h": time_delta = timedelta(hours=value)
            case "d": time_delta = timedelta(days=value)
            case "w": time_delta = timedelta(weeks=value)
            case _: time_delta = timedelta(minutes=value)
    else:
        return None

    new_datetime = current_datetime + time_delta
    return new_datetime


async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    user = message.from_user
    chat = message.chat
    member = await bot.get_chat_member(chat.id, user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.answer("❌ Вы не являетесь администратором!")
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    target_member = await bot.get_chat_member(chat.id, reply.from_user.id)
    if target_member.status in ["administrator", "creator"]:
        return await message.answer("❌ Администратор не может замутить другого администратора!")
    until_date = parse_time(command.args)
    print(parse_time(command.args))
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_messages=False)
        )
    mute_duration = format_time(command.args) if command.args else "пожизненно"
    await message.answer(f"🔇 Пользователя <b>{mention}</b> заткнули на {mute_duration}!")


async def unmute(message: Message, bot: Bot) -> Any:
    user = message.from_user
    chat = message.chat
    member = await bot.get_chat_member(chat.id, user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.answer("❌ Вы не являетесь администратором!")
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            ),
        )
    await message.answer(f"🔊 Пользователя <b>{reply.from_user.mention_html(reply.from_user.first_name)}</b> размутили!")