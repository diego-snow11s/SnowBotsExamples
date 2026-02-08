from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..storage import pending_files, pending_custom_time, file_db
from ..config import BOT_USERNAME
from ..utils.helpers import generate_code

async def handle_expiry_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in pending_files:
        await query.edit_message_text("❌ Sessão expirada. Envie o arquivo novamente.")
        return

    file_data = pending_files.pop(user_id)
    chat_id = file_data["chat_id"]
    status_id = file_data["status_msg_id"]

    if query.data == "exp_custom":
        pending_custom_time[user_id] = {
            "file_data": file_data,
            "ask_msg_id": query.message.message_id,
            "chat_id": chat_id,
        }
        await query.edit_message_text("Digite o tempo em minutos:\n(0 = nunca expira)")
        return

    if query.data == "exp_never":
        delete_after = None
        exp_str = "♾️ Permanente"
    else:
        secs = int(query.data.split("_")[1])
        delete_after = secs
        exp_str = f"{secs//60} min" if secs < 3600 else f"{secs//3600} h"

    code = generate_code(file_db)
    file_db[code] = {
        "file_id": file_data["file_id"],
        "type": file_data["type"],
        "caption": file_data["caption"],
        "delete_after": delete_after,
        "owner_id": user_id,
    }

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_id,
        text=f"✅ <b>Link Gerado!</b>\n\n"
             f"<b>Código do arquivo:</b> <code>{code}</code>\n"
             f"🔗 <code>{link}</code>\n"
             f"⏳ Expiração: {exp_str}\n\n"
             "Compartilhe com segurança!",
        parse_mode=ParseMode.HTML,
    )


async def handle_custom_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pending_custom_time:
        return

    data = pending_custom_time.pop(user_id)
    file_data = data["file_data"]

    try:
        mins = int(update.message.text.strip())
        if mins < 0:
            mins = 0
    except ValueError:
        await update.message.reply_text("❌ Envie apenas um número válido.")
        pending_custom_time[user_id] = data
        return

    delete_after = mins * 60 if mins > 0 else None
    exp_str = "♾️ Permanente" if mins == 0 else f"{mins} minutos"

    code = generate_code()
    file_db[code] = {
        "file_id": file_data["file_id"],
        "type": file_data["type"],
        "caption": file_data["caption"],
        "delete_after": delete_after,
        "owner_id": user_id,
    }

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    try:
        await context.bot.delete_message(data["chat_id"], data["ask_msg_id"])
    except:
        pass

    await update.message.reply_text(
        f"✅ <b>Link Gerado!</b>\n\n"
        f"🔗 <code>{link}</code>\n"
        f"⏳ Expiração: {exp_str}",
        parse_mode=ParseMode.HTML,
    )
