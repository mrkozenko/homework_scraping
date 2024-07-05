import os
import re

import aiofiles
from aiogram.types import Message, FSInputFile

from database.db import get_free_bot, close_db, update_bot_state, create_order, get_client_by_id, get_unfinished_orders, \
    client_exist, create_client
from services.scraping import init_bot, get_participants_count, scrape_users


async def user_check(message: Message):
    try:
        is_user_exist = await client_exist(message.from_user.id)
        if not is_user_exist:
            await create_client(message.from_user.id, message.from_user.full_name, message.from_user.username)
    except Exception as e:
        print(e)


async def add_chat_to_queue(chats, message: Message):
    try:
        client = await get_client_by_id(message.from_user.id)
        print(client)
        for chat in chats:
            try:
                await create_order(chat, client)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


