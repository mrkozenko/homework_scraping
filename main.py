import asyncio
import os

from aiogram import Router, Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from database.db import get_free_bot, init, close_db, client_exist, create_client, create_bot, get_all_bots, \
    get_all_chats
from services.middlelayer import user_check, add_chat_to_queue
from services.scraping import init_bot, get_participants_count
from dotenv import load_dotenv, dotenv_values

load_dotenv()
router = Router()
token = os.getenv("TOKEN")


@router.message(F.text, Command("info"))
async def info_message(message: Message) -> None:
    await message.reply(
        f"Бот находится на стадии beta-теста.\nНа данный момент бот способен собирать пользователей только из открытых чатов и только по публичным ссылкам.\n\nЛюбые вопросы можете задать разработчику - @Not_lax")


@router.message(F.text.startswith('/add_bot'))
async def insert_bot(message: Message) -> None:
    tokens = message.text.split("\n")[1:-1]
    for token in tokens:
        await create_bot(token)
    await message.reply("Токен успешно добавлен")


@router.message(F.text.startswith('/get_tokens'))
async def get_bots_handler(message: Message) -> None:
    tokens = await get_all_bots()
    count_tokens = len(tokens)
    await message.reply(f"{count_tokens} - count of bot tokens")

async def extract_chats(message: Message):
    chats_links = []
    chatss = await get_all_chats()
    for chat in chatss:
        try:
            chats_links.append(chat.link)
        except Exception as e:
            pass
    try:
        with open(r'chats_links.txt', 'w') as fp:
            fp.write('\n'.join(chats_links))
        await message.reply_document(document=FSInputFile("chats_links.txt"),caption=f"Chats count {len(chats_links)}")

    except Exception as e:
        print(e)
        await message.reply(f"{e}")
@router.message(F.text.startswith('/get_chats_1'))
async def get_chats_handler(message: Message) -> None:
    asyncio.create_task(extract_chats(message))



@router.message(F.text, Command("start"))
async def start_message(message: Message) -> None:
    asyncio.create_task(user_check(message))
    await message.reply(
        f"Добро пожаловать, {message.from_user.first_name} !\n\nЧтобы собрать участников открытых чатов отправьте мне ссылку на чат в одном из следующих форматов:\nhttps://t.me/club_community\n@a_community\n\nСвязь с разработчиком - @not_lax\nДополнительная информация - /info")


@router.message(F.text)
async def all_messages(message: Message):
    await message.answer(
        "Ссылка получена, начинаю обработку и сбор данных...\nОжидайте, время поиска и сбора зависит от количества участников сообщества....")
    chats = message.text.split("\n")
    asyncio.create_task(add_chat_to_queue(chats, message))


async def runner() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    # db init
    await init()
    # And the run events dispatching
    await dp.start_polling(bot)


asyncio.get_event_loop().run_until_complete(runner())
