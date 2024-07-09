from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from inline.inline import RPSKeyboard, RPSAgainKeyboard
from aiogram.types.callback_query import CallbackQuery
from settings import bot
import asyncio
import random


class RPSGame(StatesGroup):
    CHOOSING = State()
    game_timeout = None


def translate_choice(choice: str) -> str:
    if choice == "rock":
        return "камень"
    elif choice == "scissors":
        return "ножницы"
    elif choice == "paper":
        return "бумага"
    else:
        return choice


async def start_rps_game(message: types.Message, state: FSMContext) -> None:
    chat_id = message.from_user.id

    current_state = await state.get_state()
    if current_state is not None:
        return

    await message.answer("Камень, ножницы или бумага?", reply_markup=RPSKeyboard)
    await state.update_data(user_id=chat_id)
    await state.set_state(RPSGame.CHOOSING)

    async def game_timeout_callback():
        await state.clear()
        await message.answer("Время вышло, игра `Камень, ножницы или бумага` завершено")

    game_timeout = asyncio.create_task(asyncio.sleep(25))
    RPSGame.game_timeout = game_timeout
    game_timeout.add_done_callback(lambda _: asyncio.create_task(game_timeout_callback()))


async def choose_winner(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    data = await state.get_data()
    user = data.get("user_id")

    if call.from_user.id != user:
        await call.answer("Извините, только тот, кто начал игру, может выбирать.")
        return

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    user_choice = translate_choice(call.data)
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])

    if user_choice == bot_choice:
        result = "Ничья! 🤝"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
            (user_choice == 'ножницы' and bot_choice == 'бумага') or \
            (user_choice == 'бумага' and bot_choice == 'камень'):
        result = "Вы победили! 🎉"
    else:
        result = "Я победил! 😄"

    # Отправляем сообщение с результатами
    message = (
        f"{call.from_user.first_name} выбрал: {user_choice}\n"
        f"Мой выбор: {bot_choice}\n\n"
        f"{result}"
    )
    await call.message.answer(message, reply_markup=RPSAgainKeyboard)

    await state.clear()


async def play_again_rps(call: CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id

    current_state = await state.get_state()
    if current_state is not None:
        return

    await bot.delete_message(call.message.chat.id, call.message.message_id)

    await call.message.answer(
        f"{call.from_user.first_name} выбирает:\n\n"
        "Камень, ножницы или бумага?",
        reply_markup=RPSKeyboard
    )
    await state.update_data(user_id=chat_id)
    await state.set_state(RPSGame.CHOOSING)


