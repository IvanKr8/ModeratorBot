import logging
from aiogram import types
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.enums import ParseMode
from settings import bot


async def get_chat_admins(chat_id):
    try:
        logging.info(f"Trying to get administrators for chat ID: {chat_id}")
        chat_admins = await bot.get_chat_administrators(chat_id)
        logging.info(f"Chat administrators retrieved: {chat_admins}")
        admin_ids = [admin.user.id for admin in chat_admins if admin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]]
        logging.info(f"Admin IDs: {admin_ids}")
        return admin_ids
    except Exception as e:
        logging.error(f"Failed to get chat administrators: {e}")
        return []

async def report_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Вы должны ответить на сообщение пользователя, чтобы отправить репорт.")
        return

    reported_user = message.reply_to_message.from_user
    from_user = message.from_user
    chat_title = message.chat.title
    from_user_name = from_user.username or from_user.first_name
    reported_user_name = reported_user.username or reported_user.first_name
    message_id = message.reply_to_message.message_id
    message_link = f"[ссылка на сообщение](https://t.me/{message.chat.username}/{message_id})"
    message_text = message.reply_to_message.text or "недоступен"

    admin_ids = await get_chat_admins(message.chat.id)

    if reported_user.id in admin_ids:
        await message.reply("Вы не можете подать репорт на администратора.")
        return

    if from_user.id in admin_ids:
        await message.reply("Администраторы не могут подавать репорты.")
        return

    report_message = (
        f"🚨 *Репорт в чате {chat_title}* 🚨\n\n"
        f"👤 Жалоба на: {reported_user_name}\n"
        f"📩 От: {from_user_name}\n\n"
        f"Ссылка на сообщение: {message_link}\n\n"
        f"Текст сообщения:\n{message_text}"
    )

    if not admin_ids:
        await message.reply("Не удалось получить список администраторов.")
        return

    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, report_message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

    await message.reply("✅ Репорт успешно отправлен модераторам.")
