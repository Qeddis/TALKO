from aiogram import Router, F
from aiogram.types import Message

from handlers.search_utils import try_match_or_search

router = Router()


@router.message(F.text == "👦 چت با پسر")
async def search_boy(message: Message):
    await try_match_or_search(message, search_gender="پسر", require_gender_set=True)


@router.message(F.text == "👧 چت با دختر")
async def search_girl(message: Message):
    await try_match_or_search(message, search_gender="دختر", require_gender_set=True)
