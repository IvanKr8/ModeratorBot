
import asyncio
from typing import Any
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
import json
import os
from settings import BOT_BASE_DIR


WARNINGS_FILE = f'{BOT_BASE_DIR}/json/warnings.json'


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


async def load_warnings():
    try:
        with open(WARNINGS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


async def save_warnings(warnings):
    with open(WARNINGS_FILE, 'w', encoding='utf-8') as file:
        json.dump(warnings, file, ensure_ascii=False, indent=4)


async def mywarns(message: Message, bot: Bot) -> Any:
    warnings = await load_warnings()
    user_id = str(message.from_user.id)
    chat = message.chat

    if str(chat.id) in warnings and user_id in warnings[str(chat.id)]:
        warn_count = len(warnings[str(chat.id)][user_id])
        if warn_count < 3:
            await message.answer(f"⚠️ У вас {warn_count} предупреждений. Будьте осторожны, при получении 3 предупреждений вы получите мут на 24 часа.")
        elif warn_count < 5:
            await message.answer(f"⚠️ У вас {warn_count} предупреждений. Будьте осторожны, при получении 5 предупреждений вы получите мут на 72 часа.")
        else:
            await message.answer(f"⚠️ У вас {warn_count} предупреждений. Будьте осторожны, при получении 7 предупреждений вас забанят!")
    else:
        await message.answer("⚠️ У вас нет предупреждений. Продолжайте соблюдать правила, чтобы избежать наказания.")


async def reset_warnings():
    while True:
        warnings = await load_warnings()
        current_time = datetime.now()

        for chat_id, users in list(warnings.items()):
            for user_id, data in list(users.items()):
                recent_warnings = [
                    warn for warn in data
                    if current_time - datetime.strptime(warn['date'], "%Y-%m-%d %H:%M:%S.%f") <= timedelta(days=3)
                ]
                if len(recent_warnings) == 0:
                    warnings[chat_id].pop(user_id)
                    if not warnings[chat_id]:
                        warnings.pop(chat_id)
                else:
                    warnings[chat_id][user_id] = recent_warnings

        await save_warnings(warnings)
        await asyncio.sleep(1)


async def warn(message: Message, bot: Bot) -> Any:
    warnings = await load_warnings()
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
        return await message.answer("❌ Администратор не может заварнить другого администратора!")
    user_id = str(reply.from_user.id)

    if str(chat.id) not in warnings:
        warnings[str(chat.id)] = {}

    if user_id not in warnings[str(chat.id)]:
        warnings[str(chat.id)][user_id] = []

    warnings[str(chat.id)][user_id].append({"warn_number": len(warnings[str(chat.id)][user_id]) + 1, "date": str(datetime.now())})

    mention = reply.from_user.mention_html(reply.from_user.first_name)
    warn_count = len(warnings[str(chat.id)][user_id])
    if warn_count == 3:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=datetime.now() + timedelta(days=1),
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.answer(f"🔇 Пользователю <b>{mention}</b> выдан мут на 24 часа!")
    elif warn_count == 5:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=datetime.now() + timedelta(days=3),
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.answer(f"🔇 Пользователю <b>{mention}</b> выдан мут на 72 часа!")
    elif warn_count >= 7:
        warnings[str(chat.id)].pop(user_id)
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
        )
        await message.answer(f"🚫 Пользователя <b>{mention}</b> забанили!")
    else:
        await message.answer(f"⚠️ Пользователю <b>{mention}</b> выдано предупреждение!")

    await save_warnings(warnings)


async def unwarn(message: Message, bot: Bot) -> None:
    warnings = await load_warnings()
    user = message.from_user
    chat = message.chat
    reply = message.reply_to_message

    if not reply:
        await message.answer("👀 Пользователь не найден!")
        return

    user_id = str(reply.from_user.id)
    if str(chat.id) not in warnings or user_id not in warnings[str(chat.id)] or len(warnings[str(chat.id)][user_id]) == 0:
        await message.answer(f"⚠️ Пользователь {reply.from_user.mention_html(reply.from_user.first_name)} не имеет предупреждений.")
        return

    last_warn = warnings[str(chat.id)][user_id].pop()
    await save_warnings(warnings)

    await message.answer(f"✅ У пользователя {reply.from_user.mention_html(reply.from_user.first_name)} забрано предупреждение. Осталось {len(warnings[str(chat.id)][user_id])} предупреждений.")


