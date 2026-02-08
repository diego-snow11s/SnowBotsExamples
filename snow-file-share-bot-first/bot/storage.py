# Armazenamento em memória (dicionários)
file_db = {}                    # code → file info
pending_files = {}              # user_id → file_data (aguardando escolha)
pending_custom_time = {}        # user_id → {"file_data": ..., "ask_msg_id": ..., "chat_id": ...}
