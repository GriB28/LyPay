from aiogram import Router, F as mF
from aiogram.types import Message

rtr = Router()
print("SRV/manual_media_id router")


@rtr.message(mF.video, mF.from_user.id == 350531376)
async def video_id(message: Message):
    await message.answer(f"video: <code>{message.video.file_id}</code>")


@rtr.message(mF.photo, mF.from_user.id == 350531376)
async def photo_id(message: Message):
    await message.answer(f"photo: <code>{message.photo[-1].file_id}</code>")


@rtr.message(mF.document, mF.from_user.id == 350531376)
async def document_id(message: Message):
    await message.answer(f"document: <code>{message.document.file_id}</code>")


@rtr.message(mF.sticker, mF.from_user.id == 350531376)
async def sticker_id(message: Message):
    await message.answer(f"sticker: <code>{message.sticker.file_id}</code>")


@rtr.message(mF.animation, mF.from_user.id == 350531376)
async def animation_id(message: Message):
    await message.answer(f"animation: <code>{message.animation.file_id}</code>")
