import json
import sqlite3
import asyncio
import keyboards as kb
import requests
import qrcode
import os
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import InputFile
from tonsdk.utils import Address
from pytonconnect import TonConnect
from config import api_token
from support import build_bd

con = sqlite3.connect("DB.db", check_same_thread=False)
cur = con.cursor()

build_bd(cur, con)

bot = Bot(token=api_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message):
    await message.answer("Hi👋, I am an example of a bot for checking the ownership of the NFT", reply_markup=kb.Checkkb)
    await message.answer("With my help, you can check if you have an NFT from the TON Footsteps collection")
    if not cur.execute(f"SELECT id_tg FROM Users WHERE id_tg == {message.from_user.id}").fetchall():
        cur.execute(f"INSERT INTO Users (id_tg, username) VALUES ({message.from_user.id}, '{message.from_user.username}')")
        con.commit()

@dp.message_handler(text = 'Check for footstep NFT', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    if cur.execute(f"SELECT address FROM Users WHERE id_tg == {message.from_user.id}").fetchall()[0][0] is None:
        await message.answer(text="To check for the presence of NFT, connect your wallet (Tonkeeper or Tonhub)", reply_markup=kb.Walletkb)
    else:
        address = cur.execute(f"SELECT address FROM Users WHERE id_tg == {message.from_user.id}").fetchall()[0][0]
        url = f'https://tonapi.io/v2/accounts/{address}/nfts?collection=EQCV8xVdWOV23xqOyC1wAv-D_H02f7gAjPzOlNN6Nv1ksVdL&limit=1000&offset=0&indirect_ownership=false'
        try:
            response = requests.get(url).json()['nft_items']
        except:
            await message.answer(text="Something went wrong...")
            return
        if response:
            await message.answer(text="You have an NFT from the TON Footsteps collection")
        else:
            await message.answer(text="Unfortunately, you don't have NFT from the TON Footsteps collection")


@dp.message_handler(text = 'Tonkeeper', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json')
    is_connected = await connector.restore_connection()
    
    wallets_list = connector.get_wallets()

    generated_url_tonkeeper = await connector.connect(wallets_list[0])
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Open Tonkeeper', url=generated_url_tonkeeper)        
    urlkb.add(urlButton)
    img = qrcode.make(generated_url_tonkeeper)
    path = f'image{random.randint(0, 100000)}.png'
    img.save(path)
    photo = InputFile(path)
    msg = await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=urlkb)
    os.remove(path)

    flag = True
    while flag:
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                flag = False
                address = Address(connector.account.address).to_string(True, True, True)
            break
    
    await connector.disconnect()
    await msg.delete()
    await message.answer('Your wallet has been successfully connect.', reply_markup=kb.Checkkb)
    cur.execute(f"UPDATE Users SET address = '{address}' WHERE id_tg = {message.from_user.id}")
    con.commit()

@dp.message_handler(text = 'Tonhub', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonhub(message: types.Message):
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json')
    is_connected = await connector.restore_connection()
    
    wallets_list = connector.get_wallets()

    generated_url_tonhub = await connector.connect(wallets_list[1])
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Open Tonhub', url=generated_url_tonhub)
    urlkb.add(urlButton)
    img = qrcode.make(generated_url_tonhub)
    path = f'image{random.randint(0, 100000)}.png'
    img.save(path)
    photo = InputFile(path)
    msg = await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=urlkb)
    os.remove(path)

    flag = True
    while flag:
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                flag = False
                address = Address(connector.account.address).to_string(True, True, True)
            break

    await connector.disconnect()
    await msg.delete()
    await message.answer('Your wallet has been successfully connect.', reply_markup=kb.Checkkb)
    cur.execute(f"UPDATE Users SET address = '{address}' WHERE id_tg = {message.from_user.id}")
    con.commit()

@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def unknown_command(message: types.Message):
    await message.answer("unknown command⚠️")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)