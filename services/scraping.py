import asyncio
import random

from telethon import TelegramClient, functions


async def scrape_users(bot, chat, full_scraping):
    russian_letters = [chr(code) for code in range(ord('А'), ord('Я') + 1)]
    english_letters = [chr(code) for code in range(ord('A'), ord('Z') + 1)]
    common_letters = [" ", "-", "І", "."]
    letters = russian_letters + english_letters + common_letters
    usernames = set()
    phones = set()
    if not full_scraping:
        letters = [""]
    print(letters)
    for letter in letters:
        try:
            print(letter)
            async for user in bot.iter_participants(chat, search=letter):
                try:
                    #print(user)
                    if user.deleted:
                        continue
                    if not user.bot:
                        if user.username is not None:
                            usernames.add(user.username)
                        if user.phone is not None:
                            phones.add(user.phone)
                except Exception as e:
                    print(e)
                    pass
                #timeout_sleep = random.randint(0,3)
                #wait asyncio.sleep(timeout_sleep)
        except Exception as e:
            print(e)
            pass
    return usernames, phones


async def get_participants_count(bot, chat):
    # для розуміння чи потрібно парсити весь чат чи достатньо трошки(якщо юзерів мало - менше 5к)
    try:
        chat_entity = await bot(functions.channels.GetFullChannelRequest(
            channel=chat
        ))
        title = None
        try:
            title = chat_entity.chats[0].title
        except Exception as e:
            print(e)
        count = chat_entity.full_chat.participants_count
        id = chat_entity.full_chat.id
        return count,title,id
        # print(chat_entity.full_chat.participants_count)
    except Exception as e:
        print(e)
    return None,None,None


async def init_bot(token):
    api_id = 25950153
    api_hash = "cc3ce5fdb21ef5944c8bc379e0307477"
    try:
        bot = TelegramClient("bott", api_id, api_hash)
        await bot.start(bot_token=token)
    except Exception as e:
        print(f"{e}")
        return None
    return bot


#bot = asyncio.get_event_loop().run_until_complete(init_bot("6981101192:AAGZgyRVQuLOgSwyx6aRdZ7Is5Quh_wrNPU"))
#asyncio.get_event_loop().run_until_complete(get_participants_count(bot, "https://t.me/anomalygamesinc"))
