import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
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

# Текст, который будет над ссылкой
PREPARED_TEXT = "Пользователь хочет купить у вас этот подарок"

# Хорошее пожелание (при нажатии "Продать")
GOOD_WISH = (
    "Пусть этот день принесёт тебе только радость, улыбки и приятные сюрпризы!\n"
    "Желаю тебе всего самого светлого, тёплого и хорошего! ✨🎁"
)

# =======================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Как пользоваться:\n"
        "1. Просто отправь мне <b>фото</b> подарка\n"
        "2. В подписи к фото можешь сразу написать ссылку\n"
        "3. Я пришлю готовое сообщение с кнопками\n"
        "4. Перешли его человеку\n\n"
        "Пример подписи к фото:\n"
        "<code>https://t.me/nft/....</code>",
        parse_mode=ParseMode.HTML,
    )


@router.message(F.photo)
async def on_photo(message: Message):
    """
    Пользователь просто кидает фото.
    Бот берёт это фото, добавляет текст + кнопки и отправляет обратно.
    """
    # Берём самое большое фото
    photo = message.photo[-1]

    # Если пользователь написал подпись (ссылку) — используем её
    link = message.caption.strip() if message.caption else ""

    caption = PREPARED_TEXT
    if link:
        caption += f"\n{link}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Продать", callback_data="good")],
            [InlineKeyboardButton(text="Отказаться", callback_data="bad")],
        ]
    )

    # Отправляем то же самое фото + наш текст + кнопки
    await message.answer_photo(
        photo=photo.file_id,
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
