import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.enums import ParseMode

# ====================== НАСТРОЙКИ ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

# Текст, который бот подставляет вместо /go
PREPARED_TEXT = "привет как дела"

# Хорошее пожелание
GOOD_WISH = (
    "Пусть этот день принесёт тебе только радость, улыбки и приятные сюрпризы!\n"
    "Желаю тебе всего самого светлого, тёплого и хорошего! ✨🎁"
)

# Ссылка на картинку (замени на свою)
PHOTO_URL = "https://i.imgur.com/example.jpg"  # ← сюда прямую ссылку на фото

# =======================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Как пользоваться:\n"
        "1. Напиши мне команду:\n"
        "<code>/go ссылка_на_тг_подарок</code>\n\n"
        "2. Я пришлю готовое сообщение с кнопками.\n"
        "3. Перешли это сообщение человеку в личку.\n\n"
        "Когда он нажмёт кнопку — появится нужное окно.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("go"))
async def cmd_go(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "Нужно указать ссылку.\n\n"
            "Пример:\n"
            "<code>/go https://t.me/nft/....</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    link = command.args.strip()
    caption = f"{PREPARED_TEXT}\n{link}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="привет хорошо", callback_data="good")],
            [InlineKeyboardButton(text="привет плохо", callback_data="bad")],
        ]
    )

    # Отправляем фото + кнопки
    await message.answer_photo(
        photo=PHOTO_URL,
        caption=caption,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "good")
async def on_good(callback: CallbackQuery):
    await callback.answer(
        "урааа посмотри что я приготовил тебе",
        show_alert=True,
    )

    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    try:
        await callback.message.answer(GOOD_WISH)
    except Exception as e:
        logger.error(f"Не удалось отправить пожелание: {e}")


@router.callback_query(F.data == "bad")
async def on_bad(callback: CallbackQuery):
    await callback.answer(
        "увы прости",
        show_alert=True,
    )

    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
