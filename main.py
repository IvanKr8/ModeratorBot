import asyncio
import logging
import sys
from aiogram.fsm.strategy import FSMStrategy
from aiogram import Router, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, ADMINISTRATOR
from routers.mutes import mute, unmute
from routers.kick import kick
from routers.bans import ban, unban
from routers.greeting import greeting_new_member
from routers.warns import reset_warnings, warn, mywarns, unwarn
from routers.games.rps import start_rps_game, choose_winner, RPSGame, play_again_rps
from routers.help import help
from routers.report import report_user
from settings import bot

router = Router()
router.message.filter(F.chat.type == "supergroup")


async def main():
    asyncio.create_task(reset_warnings())
    dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT)
    dp.update_chat_member = True

    dp.message.register(mute, Command("mute"))
    dp.message.register(unmute, Command("unmute"))
    dp.message.register(kick, Command("kick"))
    dp.message.register(ban, Command("ban"))
    dp.message.register(unban, Command("unban"))
    dp.message.register(warn, Command("warn"))
    dp.message.register(mywarns, Command("mywarns"))
    dp.message.register(unwarn, Command("unwarn"))
    dp.message.register(help, Command("help"))
    dp.chat_member.register(greeting_new_member)
    dp.message.register(report_user, Command("report"))
    dp.message.register(start_rps_game, Command("rps"))
    dp.callback_query.register(play_again_rps, F.data == "play_rps_again")
    dp.callback_query.register(choose_winner, RPSGame.CHOOSING, F.data.in_(["rock", "scissors", "paper"]))


    # update_message = (
    #     "📢 *Обновление Бота* 📢\n\n"
    #     "В боте была добавлена новая функция:\n"
    #     "  - ➕ /rps, добавлена игра 'Камень, ножницы или бумага'"
    # )
    #
    # await bot.send_message(chat_id=-1001430255113, text=update_message, parse_mode="html")

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
