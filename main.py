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
import database
from config import api_token

# Initialize the bot with the given API token
bot = Bot(token=api_token)
# Create a dispatcher to handle incoming updates from the Telegram API
dp = Dispatcher(bot)

# Define a command handler for the '/start' command for private chats
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message):
    # Send a greeting message to the user, explaining the bot's functionality
    await message.answer("Hi👋, I am an example of a bot for checking the ownership of the NFT", reply_markup=kb.Checkkb)
    # Further explain how the bot can help with NFT collection checking
    await message.answer("With my help, you can check if you have an NFT from the TON Footsteps collection")

# Define a message handler for checking the 'footstep NFT' in private chats
@dp.message_handler(text='Check for footstep NFT', chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    # Create a storage instance based on the user's ID
    storage = database.Storage(str(message.from_user.id))

    # Initialize a connection using the given manifest URL and storage
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json', storage=storage)
    # Attempt to restore the existing connection, if any
    is_connected = await connector.restore_connection()

    # If not connected, prompt the user to connect their wallet
    if not is_connected:
        await message.answer(text="To check for the presence of NFT, connect your wallet (Tonkeeper or Tonhub)", reply_markup=kb.Walletkb)
        return

    # Retrieve the address of the connected account
    address = connector.account.address

    # Define the URL to request NFT data specific to the user's address
    url = f'https://tonapi.io/v2/accounts/{address}/nfts?collection=EQCV8xVdWOV23xqOyC1wAv-D_H02f7gAjPzOlNN6Nv1ksVdL&limit=1000&offset=0&indirect_ownership=false'

    try:
        # Send a GET request to the URL and parse the response as JSON
        response = requests.get(url).json()['nft_items']
    except:
        # If an error occurs, inform the user and exit the function
        await message.answer(text="Something went wrong...")
        return

    # If the response contains NFT items, inform the user that they have an NFT from the collection
    if response:
        await message.answer(text="You have an NFT from the TON Footsteps collection")
    else:
        # If no NFT items were found, inform the user that they don't have an NFT from the collection
        await message.answer(text="Unfortunately, you don't have NFT from the TON Footsteps collection")

# Define a message handler for connection to wallets (Tonkeeper or Tonhub) in private chats
@dp.message_handler(text=['Tonkeeper', 'Tonhub'], chat_type=types.ChatType.PRIVATE)
async def connect_wallet_tonkeeper(message: types.Message):
    # Create a storage instance based on the user's ID
    storage = database.Storage(str(message.from_user.id))
    
    # Initialize a connection using the given manifest URL and storage
    connector = TonConnect(manifest_url='https://raw.githubusercontent.com/AndreyBurnosov/Checking_for_nft_availability/main/pytonconnect-manifest.json', storage=storage)
    # Attempt to restore the existing connection, if any
    is_connected = await connector.restore_connection()

    # If already connected, inform the user and exit the function
    if is_connected:
        await message.answer('Your wallet is already connected.')
        return

    # Define the connection options for different wallet
    connection = {'Tonkeeper': 0, 'Tonhub': 2}

    # Retrieve the available wallets
    wallets_list = connector.get_wallets()

    # Generate a connection URL for the selected wallet
    generated_url_tonkeeper = await connector.connect(wallets_list[connection[message.text]])

    # Create an inline keyboard markup with a button to open the connection URL
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text=f'Open {message.text}', url=generated_url_tonkeeper)        
    urlkb.add(urlButton)
    
    # Generate a QR code for the connection URL and save it as an image
    img = qrcode.make(generated_url_tonkeeper)
    path = f'image{random.randint(0, 100000)}.png'
    img.save(path)
    photo = InputFile(path)

    # Send the QR code image to the user with the inline keyboard markup
    msg = await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=urlkb)
    # Remove the saved image from the local file system
    os.remove(path)

    # Check for a successful connection in a loop, with a maximum of 300 iterations (300 seconds)
    for i in range(300):
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                address = Address(connector.account.address).to_string(True, True, True)
            break

    # Delete the previously sent QR code message
    await msg.delete()

    # Confirm to the user that the wallet has been successfully connected
    await message.answer('Your wallet has been successfully connected.', reply_markup=kb.Checkkb)

# Entry point for the application; starts polling for updates from the Telegram API
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
