from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..storage import pending_files
from ..config import CHANNEL_ID

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not (msg.photo or msg.video or msg.document or msg.audio):
        return

    status = await msg.reply_text("⏳ Carregando e protegendo seu arquivo...")

    forwarded = await msg.forward(CHANNEL_ID)

    if forwarded.photo:
        file_id = forwarded.photo[-1].file_id
        ftype = "photo"
    elif forwarded.video:
        file_id = forwarded.video.file_id
        ftype = "video"
    elif forwarded.audio:
        file_id = forwarded.audio.file_id
        ftype = "audio"
    else:
        file_id = forwarded.document.file_id
        ftype = "document"

    user_id = msg.from_user.id
    pending_files[user_id] = {
        "file_id": file_id,
        "type": ftype,
        "caption": forwarded.caption or "",
        "status_msg_id": status.message_id,
        "chat_id": msg.chat_id,
    }

    keyboard = [
        [InlineKeyboardButton("5 min", callback_data="exp_300"),
         InlineKeyboardButton("10 min", callback_data="exp_600")],
        [InlineKeyboardButton("30 min", callback_data="exp_1800"),
         InlineKeyboardButton("1 hora", callback_data="exp_3600")],
        [InlineKeyboardButton("6 horas", callback_data="exp_21600"),
         InlineKeyboardButton("24 horas", callback_data="exp_86400")],
        [InlineKeyboardButton("♾️ Nunca", callback_data="exp_never"),
         InlineKeyboardButton("✏️ Personalizado", callback_data="exp_custom")],
    ]

    await status.edit_text(
        "✅ Arquivo carregado!\n\n"
        "⏰ Quanto tempo o arquivo deve ficar disponível?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
