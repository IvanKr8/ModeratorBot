from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter
from settings import bot


async def greeting_new_member(event: ChatMemberUpdated):
    if event.new_chat_member.status == "member":
        await bot.send_message(
            chat_id=event.chat.id,
            text=f"Добро пожаловать в наш чат, солнышко! "
                 f"Ознакомься с нашими правилами (@TFRules) и желаю тебе удачи! 🥰💜"
        )
