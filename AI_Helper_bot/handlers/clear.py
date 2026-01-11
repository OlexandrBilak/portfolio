from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.keyboard import mainmenu_keyboard
from states.states import Mode


async def clear_cmd(message: Message, state: FSMContext, messages: list):
    messages.clear()
    await state.clear()
    await state.set_state(Mode.choosing_mode)
    await message.answer('''
🧹 Історію очищено

Я видалив усю попередню історію діалогу та контекст 🗑️

ℹ️ Тепер я не памʼятаю попередні повідомлення
🔄 Ти можеш продовжити спілкування з чистого аркуша

📌 За потреби обери режим командою /mode
''', reply_markup=mainmenu_keyboard)
    
