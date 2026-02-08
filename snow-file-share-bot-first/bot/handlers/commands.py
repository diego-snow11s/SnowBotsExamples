from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..storage import file_db
from ..config import BOT_USERNAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        if code not in file_db:
            await update.message.reply_text("❌ Link inválido ou expirado.")
            return

        data = file_db[code]
        chat_id = update.effective_chat.id
        delete_after = data.get("delete_after")

        temp = await update.message.reply_text("⏳ Enviando seu arquivo...")

        if delete_after is None:
            warning = "\n\n✅ Este arquivo é <b>permanente</b> e não será excluído automaticamente."
        else:
            minutes = delete_after // 60
            warning = f"\n\n⚠️ Este arquivo será excluído em <b>{minutes} minutos</b>. Baixe agora!"

        caption = (data.get("caption") or "") + warning

        if data["type"] == "photo":
            sent = await update.message.reply_photo(data["file_id"], caption=caption, parse_mode=ParseMode.HTML)
        elif data["type"] == "video":
            sent = await update.message.reply_video(data["file_id"], caption=caption, parse_mode=ParseMode.HTML)
        elif data["type"] == "audio":
            sent = await update.message.reply_audio(data["file_id"], caption=caption, parse_mode=ParseMode.HTML)
        else:
            sent = await update.message.reply_document(data["file_id"], caption=caption, parse_mode=ParseMode.HTML)

        await temp.delete()

        if delete_after is not None:
            from .auto_delete import auto_delete_task
            context.application.create_task(auto_delete_task(context, chat_id, sent.message_id, delete_after))

        return

    await update.message.reply_text(
        f"👋 Olá, <b>{update.effective_user.first_name}</b>!\n\n"
        "Bem-vindo ao <b>Snow File Share Bot</b> — o bot mais seguro e bonito para compartilhar arquivos!\n\n"
        "Envie qualquer arquivo para começar.",
        parse_mode=ParseMode.HTML,
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Como usar o Snow File Share</b>\n\n"
        "• Envie qualquer arquivo\n"
        "• Escolha o tempo de expiração\n"
        "• Compartilhe o link gerado\n\n"
        "<b>Comandos:</b>\n"
        "/myfiles → Seus arquivos\n"
        "/revoke [código] → Apagar arquivo\n"   # mudei pra [código] ou só "código"
        "/stats → Estatísticas\n"
        "/help → Esta mensagem",
        parse_mode=ParseMode.HTML,
    )


async def myfiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_files = [(code, data) for code, data in file_db.items() if data.get("owner_id") == user_id]

    if not user_files:
        await update.message.reply_text("📭 Você ainda não tem nenhum arquivo.")
        return

    text = "📁 <b>Seus arquivos</b>\n\n"
    for code, data in user_files[:20]:
        exp = "♾️ Nunca" if data.get("delete_after") is None else f"⏳ {data['delete_after']//60} min"
        link = f"https://t.me/{BOT_USERNAME}?start={code}"
        text += f"🔗 <code>{link}</code>\n{exp}\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


async def revoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: <code>/revoke ABC12345</code>", parse_mode=ParseMode.HTML)
        return

    code = context.args[0].strip()
    user_id = update.effective_user.id

    if code in file_db and file_db[code].get("owner_id") == user_id:
        del file_db[code]
        await update.message.reply_text("✅ Arquivo removido permanentemente!")
    else:
        await update.message.reply_text("❌ Código não encontrado ou não é seu.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(file_db)
    await update.message.reply_text(f"📊 <b>Estatísticas</b>\n\nArquivos ativos: <b>{total}</b>", parse_mode=ParseMode.HTML)
    