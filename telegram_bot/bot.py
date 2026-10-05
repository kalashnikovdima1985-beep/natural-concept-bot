import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from telegram_bot.config import BOT_TOKEN, BOT_USERNAME, CHANNEL_ID, SITE_URL
from telegram_bot.keyboards import (
    get_back_keyboard,
    get_cities_keyboard,
    get_main_menu_keyboard,
    get_phone_keyboard,
    get_program_keyboard,
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FSM States for Lead Registration
class RegistrationForm(StatesGroup):
    name = State()
    phone = State()
    city = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- COMMAND HANDLERS ---

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"👋 **Вітаємо в офіційному боті курсу NATURAL CONCEPT!**\n\n"
        f"👨‍⚕️ Авторський практичний курс **Дмитра Ковальчука** з прямої реставрації передніх та бічних зубів.\n\n"
        f"✨ **Що на вас чекає:**\n"
        f"• 2 дні інтенсивної практики під мікроскопом\n"
        f"• Робота з фантомами, мікроскопами та преміальними матеріалами\n"
        f"• 📜 **Сертифікат БПР на 33 бали** (офіційно в БПР/ЕДЕБО)\n\n"
        f"Оберіть потрібний розділ у меню нижче:"
    )
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("apply"))
async def cmd_apply(message: Message, state: FSMContext):
    await start_registration(message, state)

# --- FSM LEAD REGISTRATION FLOW ---

async def start_registration(target: Message | CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationForm.name)
    msg_text = (
        "📝 **Реєстрація на практичний курс NATURAL CONCEPT**\n\n"
        "Крок 1/3: Будь ласка, введіть ваше **Ім'я та Прізвище**:"
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(msg_text, parse_mode="Markdown")
        await target.answer()
    else:
        await target.answer(msg_text, parse_mode="Markdown")

@dp.callback_query(F.data == "apply_now")
async def cb_apply_now(callback: CallbackQuery, state: FSMContext):
    await start_registration(callback, state)

@dp.message(RegistrationForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Помилка: Будь ласка, введіть коректне ім'я.")
        return
    
    await state.update_data(name=name)
    await state.set_state(RegistrationForm.phone)
    
    await message.answer(
        text=(
            f"Чудово, {name}!\n\n"
            "Крок 2/3: Надішліть ваш **номер телефону** для зв'язку.\n"
            "Натисніть кнопку нижче або введіть номер вручну (наприклад: +380971234567):"
        ),
        reply_markup=get_phone_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(RegistrationForm.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await finalize_phone(message, state, phone)

@dp.message(RegistrationForm.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    if len(phone) < 9:
        await message.answer("⚠️ Будь ласка, введіть дійсний номер телефону.")
        return
    await finalize_phone(message, state, phone)

async def finalize_phone(message: Message, state: FSMContext, phone: str):
    await state.update_data(phone=phone)
    await state.set_state(RegistrationForm.city)
    
    await message.answer(
        text=(
            "Крок 3/3: Оберіть **місто**, у якому вам зручно пройти курс:"
        ),
        reply_markup=get_cities_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(RegistrationForm.city, F.data.startswith("city_"))
async def process_city(callback: CallbackQuery, state: FSMContext):
    city_map = {
        "city_kyiv": "Київ 📍",
        "city_kharkiv": "Харків 📍",
        "city_odesa": "Одеса 📍",
        "city_other": "Інше місто 📍"
    }
    city_selected = city_map.get(callback.data, "Не вказано")
    data = await state.get_data()
    
    name = data.get("name", "Не вказано")
    phone = data.get("phone", "Не вказано")
    user_id = callback.from_user.id
    username = f"@{callback.from_user.username}" if callback.from_user.username else "Відсутній"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    await state.clear()
    
    # Send user confirmation
    user_confirm_text = (
        f"🎉 **Заявка успішно відправлена!**\n\n"
        f"👤 **ПІБ:** {name}\n"
        f"📱 **Телефон:** {phone}\n"
        f"📍 **Місто:** {city_selected}\n\n"
        f"Наш менеджер зв'яжеться з вами найближчим часом для підтвердження участі та забронює місце!"
    )
    await callback.message.answer(
        text=user_confirm_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
    
    # Notify Channel
    channel_notification = (
        f"📥 **НОВА ЗАЯВКА НА КУРС NATURAL CONCEPT!**\n\n"
        f"👤 **Клієнт:** {name}\n"
        f"📱 **Телефон:** `{phone}`\n"
        f"📍 **Обране місто:** {city_selected}\n"
        f"💬 **Telegram User:** {username} (ID: `{user_id}`)\n"
        f"⏱ **Час заявки:** {now_str}\n"
        f"🌐 **Джерело:** Telegram Bot (@{BOT_USERNAME})"
    )
    
    contact_kb = None
    if callback.from_user.username:
        contact_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написати клієнту", url=f"https://t.me/{callback.from_user.username}")]
        ])
    
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=channel_notification,
            reply_markup=contact_kb,
            parse_mode="Markdown"
        )
        logger.info(f"Successfully posted lead for {name} to channel {CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to post lead to channel {CHANNEL_ID}: {e}")

@dp.callback_query(F.data == "cancel_reg")
async def cb_cancel_reg(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Реєстрацію скасовано.", reply_markup=get_main_menu_keyboard())
    await callback.answer()

# --- CONTENT CALLBACK HANDLERS ---

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="Головне меню курсу NATURAL CONCEPT:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "course_program")
async def cb_course_program(callback: CallbackQuery):
    program_text = (
        "📚 **Програма курсу NATURAL CONCEPT (2 дні)**\n\n"
        "Практичний курс охоплює всі аспекти сучасної прямої естетичної реставрації:\n\n"
        "🔹 **День 1: Реставрація передньої групи зубів**\n"
        "• Анатомія, оптичні властивості та морфологія фронтальних зубів\n"
        "• Стратифікація та вибір відтінків композиту\n"
        "• Оформлення контактних пунктів та мікрорельєфу\n"
        "• Протоколи полірування до дзеркального блиску\n\n"
        "🔹 **День 2: Реставрація бічної групи зубів**\n"
        "• Оклюзійний компас та моделювання жувальних поверхонь\n"
        "• Контроль C-фактора та зниження усадки\n"
        "• Консервативне препарування та ізоляція раббердамом\n"
        "• Швидкі та надійні техніки відтворення горбів\n\n"
        "Оберіть день для детального знайомства або залишіть заявку:"
    )
    await callback.message.edit_text(
        text=program_text,
        reply_markup=get_program_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "program_day1")
async def cb_program_day1(callback: CallbackQuery):
    day1_text = (
        "🔹 **День 1: Фронтальна група (Передні зуби)**\n\n"
        "📖 **Теоретичний блок:**\n"
        "1. Анализ формату та оптичної структури емалі й дентину.\n"
        "2. Вибір композитних систем та техніка шарування.\n"
        "3. Крайове прилягання та фрезерування фаски.\n\n"
        "🔬 **Практична частина под мікроскопом:**\n"
        "• Відтворення прозорого краю, мамелонів та гіпоплазій.\n"
        "• Контурування, створення текстури та мікрорельєфу.\n"
        "• Покроковий фініш та фінішна поліровка.\n"
    )
    await callback.message.edit_text(
        text=day1_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "program_day2")
async def cb_program_day2(callback: CallbackQuery):
    day2_text = (
        "🔹 **День 2: Жувальна група (Бічні зуби)**\n\n"
        "📖 **Теоретичний блок:**\n"
        "1. Морфологічний аналіз молярів та премолярів.\n"
        "2. Оклюзійна висота, контакти та передчасно встановлені контакти.\n"
        "3. Секрети роботи з матричними системами та клинами.\n\n"
        "🔬 **Практична частина под мікроскопом:**\n"
        "• Моделювання фісур 1 та 2 порядку.\n"
        "• Відтворення щільної контактної стінки.\n"
        "• Крайовий адаптаційний шар та контрольована полімеризація.\n"
    )
    await callback.message.edit_text(
        text=day2_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "about_author")
async def cb_about_author(callback: CallbackQuery):
    author_text = (
        "👨‍⚕️ **Про лектора курса: Дмитро Ковальчук**\n\n"
        "• Практикуючий стоматолог-реставратор із понад 10-річним досвідом.\n"
        "• Засновник навчальної методики **NATURAL CONCEPT**.\n"
        "• Спікер міжнародних стоматологічних симпозіумів та конгресів.\n"
        "• Навчив понад 1,500+ стоматологів технікам високоточного відновлення зубів під мікроскопом.\n\n"
        "💡 *«Головна мета Natural Concept — навчити лікаря бачити природну анатомію та повторювати її з першого разу без тривалого пришліфовування.»*"
    )
    await callback.message.edit_text(
        text=author_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "dates_cities")
async def cb_dates_cities(callback: CallbackQuery):
    dates_text = (
        "📅 **Найближчий розклад курсів NATURAL CONCEPT:**\n\n"
        "📍 **Київ**\n"
        "🗓 14-15 Листопада | 🟢 Є вільні місця\n\n"
        "📍 **Харків**\n"
        "🗓 28-29 Листопада | 🟡 Залишилось 3 місця\n\n"
        "📍 **Одеса**\n"
        "🗓 12-13 Грудня | 🟢 Є вільні місця\n\n"
        "⏱ Кількість місць у кожній групі обмежена до 10 осіб для максимальної практичної віддачі!"
    )
    await callback.message.edit_text(
        text=dates_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "bpr_info")
async def cb_bpr_info(callback: CallbackQuery):
    bpr_text = (
        "🎓 **Сертифікат БПР на 33 бали**\n\n"
        "Курс NATURAL CONCEPT офіційно атестований у системі Безперервного Професійного Розвитку (БПР) лікарів України.\n\n"
        "📜 **Що ви отримуєте:**\n"
        "1. Офіційний іменний Сертифікат із унікальним QR-кодом.\n"
        "2. Нарахування **33 балів БПР** для атестації лікаря.\n"
        "3. Внесення даних до реєстру ЕДЕБО.\n"
    )
    await callback.message.edit_text(
        text=bpr_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def main():
    logger.info("Starting Natural Concept Telegram Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
