import asyncio
from .loader import build_application
from .utils.helpers import logger

def main():
    app = build_application()
    logger.info("✅ Snow File Share Bot está online!")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
