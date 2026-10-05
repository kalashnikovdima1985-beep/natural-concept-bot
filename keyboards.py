from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram_bot.config import SITE_URL

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📝 Залишити заявку на курс", callback_data="apply_now")],
        [InlineKeyboardButton(text="📚 Програма курсу", callback_data="course_program")],
        [InlineKeyboardButton(text="👨‍⚕️ Про лектора (Дмитро Ковальчук)", callback_data="about_author")],
        [InlineKeyboardButton(text="📅 Розклад та міста", callback_data="dates_cities")],
        [InlineKeyboardButton(text="🎓 Сертифікат БПР (33 бали)", callback_data="bpr_info")],
        [InlineKeyboardButton(text="🌐 Відкрити сайт Natural Concept", url=SITE_URL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_program_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🔹 День 1: Передні зуби (Фронтальна група)", callback_data="program_day1")],
        [InlineKeyboardButton(text="🔹 День 2: Бічні зуби (Жувальна група)", callback_data="program_day2")],
        [InlineKeyboardButton(text="📝 Залишити заявку", callback_data="apply_now")],
        [InlineKeyboardButton(text="🔙 Головне меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_cities_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📍 Київ", callback_data="city_kyiv"), InlineKeyboardButton(text="📍 Харків", callback_data="city_kharkiv")],
        [InlineKeyboardButton(text="📍 Одеса", callback_data="city_odesa"), InlineKeyboardButton(text="📍 Інше місто", callback_data="city_other")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_reg")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    button = KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)

def get_back_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📝 Залишити заявку", callback_data="apply_now")],
        [InlineKeyboardButton(text="🔙 Головне меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
