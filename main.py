import sqlite3
import asyncio
import requests
import qrcode
import os
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import InputFile
from tonsdk.utils import Address
from pytonconnect import TonConnect

import keyboards as kb
from config import api_token
from support import build_bd


# Establishing a connection to the SQLite database named 'DB.db' and creating a cursor.

con = sqlite3.connect("DB.db", check_same_thread=False)
cur = con.cursor()

build_bd(cur, con)

# Creating a Telegram Bot instance and a Dispatcher object for message handling.

# Creating a Bot instance using the 'api_token' provided.
bot = Bot(token=api_token)

# Creating a Dispatcher instance associated with the Bot instance.
dp = Dispatcher(bot)

# This message handler is triggered when a user sends the '/start' command in a private chat with the bot.

@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message):
    # Sends a welcome message to the user, introducing the bot's purpose and functionality.
    await message.answer("Hi👋, I am an example of a bot for checking the ownership of the NFT", reply_markup=kb.Checkkb)
    await message.answer("With my help, you can check if you have an NFT from the TON Footsteps collection")

    # Checks if the user's Telegram ID is already present in the 'Users' database table.
    # If not, it adds the user's ID and username to the 'Users' table as a new entry.
    if not cur.execute(f"SELECT id_tg FROM Users WHERE id_tg == {message.from_user.id}").fetchall():
        cur.execute(f"INSERT INTO Users (id_tg, username) VALUES ({message.from_user.id}, '{message.from_user.username}')")
        con.commit()

# A message handler function to check if the user has a footstep NFT and respond accordingly.

@dp.message_handler(text='Check for footstep NFT', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    # Checking if the user's wallet address is present in the database for the given Telegram ID.
    # If the address is not available, prompt the user to connect their wallet (Tonkeeper or Tonhub).
    if cur.execute(f"SELECT address FROM Users WHERE id_tg == {message.from_user.id}").fetchall()[0][0] is None:
        await message.answer(text="To check for the presence of NFT, connect your wallet (Tonkeeper or Tonhub)", reply_markup=kb.Walletkb)
    else:
        # If the user's wallet address is available, proceed to check for the presence of the footstep NFT.
        address = cur.execute(f"SELECT address FROM Users WHERE id_tg == {message.from_user.id}").fetchall()[0][0]
        
        # Forming the URL to query the TON API for the user's NFTs from the TON Footsteps collection.
        url = f'https://tonapi.io/v2/accounts/{address}/nfts?collection=EQCV8xVdWOV23xqOyC1wAv-D_H02f7gAjPzOlNN6Nv1ksVdL&limit=1000&offset=0&indirect_ownership=false'
        
        try:
            # Sending a GET request to the TON API and parsing the JSON response to extract NFT items.
            response = requests.get(url).json()['nft_items']
        except:
            # If there's an error with the API request, notify the user.
            await message.answer(text="Something went wrong...")
            return
        
        # Based on the response from the TON API, informing the user about the NFT presence or absence.
        if response:
            await message.answer(text="You have an NFT from the TON Footsteps collection")
        else:
            await message.answer(text="Unfortunately, you don't have NFT from the TON Footsteps collection")


# A message handler function to connect the user's Tonkeeper wallet to the bot.

@dp.message_handler(text='Tonkeeper', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    # Creating a TonConnect instance and restoring the connection to Tonkeeper using the provided manifest URL.
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json')
    is_connected = await connector.restore_connection()
    
    # Getting a list of available wallets from the TonConnect instance.
    wallets_list = connector.get_wallets()

    # Connecting the user's Tonkeeper wallet and generating a connection URL.
    generated_url_tonkeeper = await connector.connect(wallets_list[0])
    
    # Creating an inline keyboard markup with a URL button to open Tonkeeper and a QR code for the connection URL.
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Open Tonkeeper', url=generated_url_tonkeeper)        
    urlkb.add(urlButton)
    img = qrcode.make(generated_url_tonkeeper)
    path = f'image{random.randint(0, 100000)}.png'
    img.save(path)
    photo = InputFile(path)
    
    # Sending the QR code as a photo along with the URL button to open Tonkeeper.
    msg = await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=urlkb)
    os.remove(path)

    # Continuously checking if the connection to Tonkeeper is successful and obtaining the user's wallet address.
    flag = True
    while flag:
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                flag = False
                address = Address(connector.account.address).to_string(True, True, True)
            break

    # Disconnecting the TonConnect instance after obtaining the user's wallet address.
    await connector.disconnect()
    
    # Deleting the photo message that contained the QR code to keep the chat clean.
    await msg.delete()
    
    # Informing the user that their wallet has been successfully connected and providing a new keyboard.
    await message.answer('Your wallet has been successfully connected.', reply_markup=kb.Checkkb)
    
    # Updating the user's address in the database with the obtained wallet address.
    cur.execute(f"UPDATE Users SET address = '{address}' WHERE id_tg = {message.from_user.id}")
    con.commit()

# A message handler function to connect the user's Tonhub wallet to the bot.

@dp.message_handler(text='Tonhub', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonhub(message: types.Message):
    # Creating a TonConnect instance and restoring the connection to Tonhub using the provided manifest URL.
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json')
    is_connected = await connector.restore_connection()
    
    # Getting a list of available wallets from the TonConnect instance.
    wallets_list = connector.get_wallets()

    # Connecting the user's Tonhub wallet and generating a connection URL.
    generated_url_tonhub = await connector.connect(wallets_list[1])
    
    # Creating an inline keyboard markup with a URL button to open Tonhub and a QR code for the connection URL.
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Open Tonhub', url=generated_url_tonhub)
    urlkb.add(urlButton)
    img = qrcode.make(generated_url_tonhub)
    path = f'image{random.randint(0, 100000)}.png'
    img.save(path)
    photo = InputFile(path)
    
    # Sending the QR code as a photo along with the URL button to open Tonhub.
    msg = await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=urlkb)
    os.remove(path)

    # Continuously checking if the connection to Tonhub is successful and obtaining the user's wallet address.
    flag = True
    while flag:
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                flag = False
                address = Address(connector.account.address).to_string(True, True, True)
            break

    # Disconnecting the TonConnect instance after obtaining the user's wallet address.
    await connector.disconnect()
    
    # Deleting the photo message that contained the QR code to keep the chat clean.
    await msg.delete()
    
    # Informing the user that their wallet has been successfully connected and providing a new keyboard.
    await message.answer('Your wallet has been successfully connected.', reply_markup=kb.Checkkb)
    
    # Updating the user's address in the database with the obtained wallet address.
    cur.execute(f"UPDATE Users SET address = '{address}' WHERE id_tg = {message.from_user.id}")
    con.commit()


@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def unknown_command(message: types.Message):
    await message.answer("unknown command⚠️")

# The main entry point of the Telegram bot application.

if __name__ == '__main__':
    # Start polling for updates from the Telegram Bot API using the executor.
    # The `dp` (Dispatcher) object handles message handling and other event processing.
    # The `skip_updates=True` parameter tells the executor to skip pending updates when starting.
    executor.start_polling(dp, skip_updates=True)