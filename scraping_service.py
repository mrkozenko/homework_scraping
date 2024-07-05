import asyncio
import os
import random

import aiofiles
import re

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from database.db import get_unfinished_orders, get_free_bot, update_bot_state, add_chat, update_order, init
from database.models import Queue
from services.scraping import init_bot, get_participants_count, scrape_users

load_dotenv()
token_bot_main = os.getenv("TOKEN")
bot = Bot(token_bot_main, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def scraping_community():
    await init()
    while True:
        orders = await get_unfinished_orders()
        print(orders)
        if orders:
            for order in orders:
                try:
                    print("order")
                    asyncio.create_task(scraping_thread(order))
                    await asyncio.sleep(7)
                except Exception as e:
                    print(e)
            await asyncio.sleep(15)
    print("all?")
    return 1


async def scraping_thread(order: Queue):
    bot_client = None
    phones, usernames = None, None
    token = None
    bot_instance = None
    try:

        bot_token = await get_free_bot()
        if bot_token is not None:
            token = bot_token.token
            bot_instance = bot_token
            bot_client = await init_bot(token)
            print(order.chat_url)
            await update_order(order.id,bot_instance,"in_progress")
            await update_bot_state(token, True)
            receive_client_id = await order.client.first()
            receive_client_id = receive_client_id.id
            count, title, id = await get_participants_count(bot_client, order.chat_url)
            if count is None and title is None and id is None:
                await bot.send_message(
                    text=f"Проверьте тип сообщества, нам не удалось получить участников... ;(\n",
                    chat_id=receive_client_id)
                try:
                    await bot_client.disconnect()
                except Exception as e:
                    print(e)
                await update_bot_state(token, False)
                await update_order(order_id=order.id, bot=bot_instance, status="fail")
                return 0
            invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
            # Заміна неприйнятних символів на підкреслення (_)
            clear_path_report = re.sub(invalid_chars, '', title)
            if count is not None:
                await add_chat(id=id, title=title, link=order.chat_url)
                await bot.send_message(
                    text=f"<b>Начинаю собирать пользователей чата - {title}</b>\nВ чате всего - {count} участников.\n",
                    chat_id=receive_client_id)
                print(count)
                if count > 13000:
                    usernames, phones = await scrape_users(bot_client, order.chat_url, full_scraping=True)
                else:
                    usernames, phones = await scrape_users(bot_client, order.chat_url, full_scraping=False)

                if usernames is None and phones is None:
                    await bot.send_message(
                        text=f"Проверьте тип сообщества, нам не удалось получить участников... ;(\n",
                        chat_id=receive_client_id)
                    try:
                        await bot_client.disconnect()
                    except Exception as e:
                        print(e)
                    await update_bot_state(token, False)
                    await update_order(order_id=order.id, bot=bot_instance, status="fail")

                    return 0
                usernames_txt_caption = f"{clear_path_report}_usernames.txt"
                phones_txt_caption = f"{clear_path_report}_phones.txt"
                filename_phones = await make_report(phones, phones_txt_caption)
                filename_usernames = await make_report(usernames, usernames_txt_caption)
                await bot.send_document(chat_id=receive_client_id,caption=f"Ники:{len(usernames)}",
                                        document=FSInputFile(usernames_txt_caption))
                await bot.send_document(chat_id=receive_client_id,caption=f"Номера:{len(phones)}",
                                        document=FSInputFile(phones_txt_caption))

                await clear_files([usernames_txt_caption, phones_txt_caption])
                await update_order(order_id=order.id, bot=bot_instance, status="done")
                try:
                    await bot_client.disconnect()
                except Exception as e:
                    print(e)
                await update_bot_state(token, False)
            else:
                print("why none count")
                pass
        else:
            print("NOT FOUND FREE BOT")

    except Exception as e:
        await update_bot_state(token, False)
        await update_order(order_id=order.id, bot=bot_instance, status="fail")
        try:
            await bot_client.disconnect()
        except Exception as e:
            print(e)
        print(e)


async def clear_files(filenames: list):
    for filename in filenames:
        try:
            await os.remove(filename)
        except:
            pass


async def make_report(data_set: set, path: str):
    # return filename
    try:
        async with aiofiles.open(path, mode='w') as file:
            data = "\n".join(data_set)
            await file.write(data + "\n")
    except Exception as e:
        pass


asyncio.get_event_loop().run_until_complete(scraping_community())
