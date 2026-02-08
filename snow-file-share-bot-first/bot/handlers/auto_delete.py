import asyncio
import logging

logger = logging.getLogger(__name__)

async def auto_delete_task(context, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.info(f"Falha ao deletar mensagem {message_id}: {e}")
