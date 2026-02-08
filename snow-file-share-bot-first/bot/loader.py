from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from .handlers.commands import start, help_cmd, myfiles, revoke, stats
from .handlers.upload import handle_upload
from .handlers.expiry import handle_expiry_choice, handle_custom_time
from .config import BOT_TOKEN

def build_application():
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("myfiles", myfiles))
    app.add_handler(CommandHandler("revoke", revoke))
    app.add_handler(CommandHandler("stats", stats))

    # Upload de arquivos
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL,
        handle_upload
    ))

    # Callbacks e texto custom
    app.add_handler(CallbackQueryHandler(handle_expiry_choice, pattern="^exp_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_time))

    return app
