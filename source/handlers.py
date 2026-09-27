import os
import shutil
import tempfile
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import INCLUDE_DIR
from compiler import compile_pawn, decompile_pawn
from keyboards import get_main_menu_keyboard, get_done_include_keyboard

router = Router()

class BotStates(StatesGroup):
    waiting_for_mode_file = State()
    waiting_for_inc = State()

@router.message(Command("gamemodes"))
async def cmd_gamemodes(message: Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_mode_file)
    await message.answer("Отправьте файл `.pwn` (для компиляции) или `.amx` (для декомпиляции) документом.", parse_mode="Markdown")

@router.message(Command("include"))
async def cmd_include(message: Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_inc)
    await state.update_data(uploaded_count=0)
    await message.answer(
        "Отправляйте файлы `.inc` документом (можно сразу несколько).\nКогда закончите, нажмите кнопку ниже.",
        reply_markup=get_done_include_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "act_gamemodes")
async def cb_gamemodes(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.waiting_for_mode_file)
    await call.message.answer("Отправьте файл `.pwn` (для компиляции) или `.amx` (для декомпиляции) документом.", parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "act_include")
async def cb_include(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.waiting_for_inc)
    await state.update_data(uploaded_count=0)
    await call.message.answer(
        "Отправляйте файлы `.inc` документом (можно сразу несколько).\nКогда закончите, нажмите кнопку ниже.",
        reply_markup=get_done_include_keyboard(),
        parse_mode="Markdown"
    )
    await call.answer()

@router.callback_query(F.data == "finish_include")
async def cb_finish_include(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    count = data.get("uploaded_count", 0)
    await state.clear()
    await call.message.answer(f"Загрузка завершена. Всего сохранено файлов: *{count}*", parse_mode="Markdown")
    await call.answer()

@router.message(BotStates.waiting_for_mode_file, F.document)
async def handle_mode_upload(message: Message, state: FSMContext, bot: Bot):
    doc = message.document
    filename = doc.file_name.lower()
    
    is_pwn = filename.endswith('.pwn')
    is_amx = filename.endswith('.amx')

    if not (is_pwn or is_amx):
        await message.answer("Ошибка: принимаются только файлы `.pwn` или `.amx`", parse_mode="Markdown")
        return

    await state.clear()
    action_str = "Компиляция" if is_pwn else "Декомпиляция"
    status = await message.answer(f"Файл получен. Выполняется {action_str.lower()}...")

    temp_dir = tempfile.mkdtemp()
    file_base = os.path.splitext(doc.file_name)[0]
    input_path = os.path.join(temp_dir, doc.file_name)

    try:
        file_info = await bot.get_file(doc.file_id)
        await bot.download_file(file_info.file_path, input_path)

        if is_pwn:
            success, logs, out_path = await compile_pawn(input_path, file_base)
            target_ext = "amx"
        else:
            success, logs, out_path = await decompile_pawn(input_path, file_base)
            target_ext = "pwn"

        formatted_logs = f"```\n{logs[:3500]}\n```" if logs else "_Лог операции пуст._"

        if success and out_path:
            out_file = FSInputFile(out_path, filename=f"{file_base}_result.{target_ext}")
            await message.answer_document(out_file, caption=f"Успешно! [{action_str}]\n\n{formatted_logs}", parse_mode="Markdown")
        else:
            await message.answer(f"Ошибка операции ({action_str}):\n\n{formatted_logs}", parse_mode="Markdown")

    finally:
        await status.delete()
        shutil.rmtree(temp_dir, ignore_errors=True)

@router.message(BotStates.waiting_for_inc, F.document)
async def handle_inc_upload(message: Message, state: FSMContext, bot: Bot):
    doc = message.document
    if not doc.file_name.lower().endswith('.inc'):
        await message.answer("Ошибка: принимаются только файлы `.inc`", parse_mode="Markdown")
        return

    target_path = os.path.join(INCLUDE_DIR, doc.file_name)

    try:
        file_info = await bot.get_file(doc.file_id)
        await bot.download_file(file_info.file_path, target_path)
        
        data = await state.get_data()
        current_count = data.get("uploaded_count", 0) + 1
        await state.update_data(uploaded_count=current_count)

        await message.answer(
            f"Инклуд `{doc.file_name}` сохранён! (Загружено: {current_count})",
            reply_markup=get_done_include_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"Ошибка загрузки `{doc.file_name}`: `{e}`", parse_mode="Markdown")

@router.message(BotStates.waiting_for_mode_file)
async def invalid_mode_input(message: Message):
    await message.answer("Ожидается документ `.pwn` или `.amx`. Пожалуйста, отправьте файл.", parse_mode="Markdown")

@router.message(BotStates.waiting_for_inc)
async def invalid_inc_input(message: Message):
    await message.answer("Ожидается документ `.inc`. Нажмите кнопку 'Завершить загрузку', если вы закончили.", reply_markup=get_done_include_keyboard(), parse_mode="Markdown")

@router.message(F.text.startswith('/'))
async def fallback_commands(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Команда не найдена. Выберите необходимое действие из списка:",
        reply_markup=get_main_menu_keyboard()
    )
