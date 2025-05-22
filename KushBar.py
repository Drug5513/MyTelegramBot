from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token="7863869683:AAHbskO6rwLfPTReQRH3GjzmzqKAsqzmHfg")
dp = Dispatcher(bot)

menu_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
menu_buttons.add(
    KeyboardButton('Прайс'),
    KeyboardButton('Бонусы'),
    KeyboardButton('Последний заказ'),
)
menu_buttons.add(
    KeyboardButton('Отзывы 0 (0)'),
    KeyboardButton('Оператор')
)

@dp.message_handler(commands=['start', 'menu'])
async def send_menu(message: types.Message):
    await message.answer("Выберите пункт меню:", reply_markup=menu_buttons)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)