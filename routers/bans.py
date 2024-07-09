from typing import Any
from contextlib import suppress

from aiogram import Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from routers.mutes import parse_time


async def unban(message: Message, bot: Bot) -> Any:
    user = message.from_user
    chat = message.chat
    member = await bot.get_chat_member(chat.id, user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.answer("❌ Вы не являетесь администратором!")
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    with suppress(TelegramBadRequest):
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=reply.from_user.id)
    await message.answer(f"✅ Пользователя <b>{reply.from_user.mention_html(reply.from_user.first_name)}</b> разбанили!")


async def ban(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
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
        return await message.answer("❌ Администратор не может забанить другого администратора!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)
    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id, user_id=reply.from_user.id, until_date=until_date
        )
    await message.answer(f"🚫 Пользователя <b>{mention}</b> забанили!")