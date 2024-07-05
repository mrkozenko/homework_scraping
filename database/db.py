import random

from tortoise import Tortoise, run_async

from database.models import Client, Bot, Queue, Chat


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['database.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


async def close_db():
    try:
        await Tortoise.close_connections()
    except Exception as e:
        print(e)


async def client_exist(id: int):
    try:
        is_exist = await Client.filter(id=id).exists()
        return is_exist
    except Exception as e:
        return False


async def create_client(id: int, name: str, username: str):
    try:
        await Client.create(id=id, fullname=name, username=username)
    except Exception as e:
        print(e)

async def create_bot(token:str):
    try:
        await Bot.create(token=token)
    except Exception as e:
        print(e)

async def delete_client(id: int):
    try:
        await Client.filter(id=id).delete()
    except Exception as e:
        print(e)


async def delete_bot(id: int):
    try:
        await Bot.filter(id=id).delete()
    except Exception as e:
        print(e)

async def get_all_chats():
    try:
        chats = await Chat.all()
        return chats
    except Exception as e:
        print(e)

async def get_all_bots():
    try:
        bots = await Bot.all()
        return bots
    except Exception as e:
        print(e)


async def get_all_clients():
    try:
        clients = await Client.all()
        await create_order("sss", clients[0])
        return clients
    except Exception as e:
        print(e)
        return None


async def get_all_orders():
    # повертає замовлення на парсинг
    try:
        orders = await Queue.all()
        return orders
    except Exception as e:
        print(e)
        return None


async def create_order(chat_url: str, client: Client):
    # повертає замовлення на парсинг
    try:
        order = await Queue.create(chat_url=chat_url, client=client,status="in_order")
        return order
    except Exception as e:
        print(e)
        return None


async def update_order(order_id: int, bot: Bot, status: str):
    try:
        await Queue.filter(id=order_id).update(status=status, bot=bot)
    except Exception as e:
        return None


async def get_done_orders():
    try:
        return await Queue.filter(status="done").all()
    except Exception as e:
        return None


async def get_unfinished_orders():
    try:
        return await Queue.filter(status="in_order").all()
    except Exception as e:
        return None


async def get_free_bot():
    # get random free bot, not busy
    # or return None
    try:
        bots = await Bot.filter(is_busy=False)
        print(bots)
        if bots:
            random_bot = random.choice(bots)
            print(random_bot)
            return random_bot
        else:
            return None
    except Exception as e:
        return None


async def update_bot_state(token, status):
    try:
        await Bot.filter(token=token).update(is_busy=status)
    except Exception as e:
        print(e)


async def get_client_by_id(client_id):
    try:
        client = await Client.filter(id=client_id).first()
        return client
    except Exception as e:
        print(e)
        return None


async def chat_exist(id: int):
    try:
        is_exist = await Chat.filter(id=id).exists()
        return is_exist
    except Exception as e:
        return False


async def create_chat(id: int, title: str, link: str):
    try:
        await Chat.create(id=id, title=title, link=link)
    except Exception as e:
        print(e)


async def add_chat(id, title, link):
    is_exist = await chat_exist(id)
    if not is_exist:
        await create_chat(id, title, link)
