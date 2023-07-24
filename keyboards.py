from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CheckButton = KeyboardButton('Check for footstep NFT')

Checkkb = ReplyKeyboardMarkup(resize_keyboard=True).add(CheckButton)

TonkeeperButton = KeyboardButton('Tonkeeper')
TonhubButton = KeyboardButton('Tonhub')

Walletkb = ReplyKeyboardMarkup(resize_keyboard=True).add(TonkeeperButton).add(TonhubButton)