from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, create_user, update_balance
from bot.keyboards import main_menu, confirm_payment_keyboard
from services.parser import parse_ebay_item
from config import CHECK_PRICE, MIN_DEPOSIT

router = Router()

# FSM для проверки товара
class CheckStates(StatesGroup):
    waiting_for_id = State()
    confirm_payment = State()

# FSM для пополнения баланса
class DepositStates(StatesGroup):
    waiting_for_amount = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        await create_user(message.from_user.id)
    await message.answer("Добро пожаловать в бот проверки товаров.", reply_markup=main_menu())

@router.message(lambda message: message.text == "Баланс")
async def balance_handler(message: Message):
    user = await get_user(message.from_user.id)
    balance = user[2]
    await message.answer(f"Ваш баланс: ${balance}")

@router.message(lambda message: message.text == "Пополнить баланс")
async def deposit_balance(message: Message, state: FSMContext):
    await message.answer(f"Введите сумму пополнения (минимум ${MIN_DEPOSIT}):")
    await state.set_state(DepositStates.waiting_for_amount)

@router.message(DepositStates.waiting_for_amount)
async def process_deposit(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer("Некорректная сумма. Введите число.")
        return
    if amount < MIN_DEPOSIT:
        await message.answer(f"Минимальная сумма пополнения — ${MIN_DEPOSIT}")
        return
    await update_balance(message.from_user.id, amount)
    await message.answer(f"Баланс успешно пополнен на ${amount}")
    await state.clear()

@router.message(lambda message: message.text == "Проверить товар")
async def check_product(message: Message, state: FSMContext):
    await message.answer(f"Отправьте ID товара для проверки.\n\nСтоимость проверки: ${CHECK_PRICE}")
    await state.set_state(CheckStates.waiting_for_id)

@router.message(CheckStates.waiting_for_id)
async def process_item_id(message: Message, state: FSMContext):
   
    item_id = message.text.strip()
    await state.update_data(item_id=item_id)

    user = await get_user(message.from_user.id)

    if user[2] < CHECK_PRICE:
        await message.answer("Недостаточно средств. Пополните баланс.")
        await state.clear()
        return

    await message.answer(
        f"Стоимость проверки: ${CHECK_PRICE}\nВыберите действие ниже:",
        reply_markup=confirm_payment_keyboard()
    )

    await state.set_state(CheckStates.confirm_payment)

@router.message(CheckStates.confirm_payment)
async def confirm_check(message: Message, state: FSMContext):
    if message.text.lower() != "подтвердить":
        await message.answer("Проверка отменена.")
        await state.clear()
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    await update_balance(message.from_user.id, -CHECK_PRICE)
    result = parse_ebay_item(item_id)
    await message.answer(
        f"Результат проверки:\n\n"
        f"Название: {result['title']}\n"
        f"Цена: {result['price']}\n"
        f"Наличие: {result['availability']}\n"
        f"Списано: ${CHECK_PRICE}"
    )
    await state.clear()


@router.callback_query(lambda c: c.data == "confirm_payment")
async def confirm_check_callback(callback: CallbackQuery, state: FSMContext):

    user = await get_user(callback.from_user.id)
    if user[2] < CHECK_PRICE:
        await callback.message.edit_text("Недостаточно средств. Пополните баланс.")
        await state.clear()
        return

    data = await state.get_data()
    item_id = data.get("item_id")

    # списание средств
    await update_balance(callback.from_user.id, -CHECK_PRICE)

    # парсинг товара
    from services.parser import parse_ebay_item
    result = parse_ebay_item(item_id)

    await callback.message.edit_text(
        f"Результат проверки:\n\n"
        f"Название: {result['title']}\n"
        f"Цена: {result['price']}\n"
        f"Наличие: {result['availability']}\n"
        f"Списано: ${CHECK_PRICE}"
    )

    await state.clear()


@router.callback_query(lambda c: c.data == "cancel_payment")
async def cancel_check_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Проверка отменена пользователем.")
    await state.clear()