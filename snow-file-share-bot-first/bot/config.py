from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "NomeDoSeuBot")  # Substitua pelo nome de usuário do seu bot, sem o @.
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1000000000000"))  # Substitua pelo ID do seu canal privado.

BASE_DIR = Path(__file__).resolve().parent.parent
