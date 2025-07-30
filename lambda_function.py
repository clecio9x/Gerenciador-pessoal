import json
import os
import requests

# Carrega as variáveis de ambiente
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DJANGO_API_KEY = os.environ.get('DJANGO_API_KEY')
DJANGO_NOTE_API_URL = os.environ.get('DJANGO_NOTE_API_URL')
DJANGO_LINK_API_URL = os.environ.get('DJANGO_LINK_API_URL')
DJANGO_UNLINK_API_URL = os.environ.get('DJANGO_UNLINK_API_URL') # <-- NOVA
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def lambda_handler(event, context):
    try:
        # ... (código de extração de mensagem, chat_id, text continua o mesmo)
        body_str = event.get('body')
        if not body_str: return {'statusCode': 200}
        data = json.loads(body_str)
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()

        if not chat_id: return {'statusCode': 200}
        
        # --- LÓGICA DE COMANDOS ATUALIZADA ---
        
        if text == '/start':
            reply_message = "Olá! Bem-vindo ao KeyCrypt Bot. Para vincular sua conta, vá ao seu perfil no nosso site e use o comando /vincular."

        elif text.startswith('/vincular '):
            token = text.replace('/vincular ', '', 1).strip()
            headers = {'Authorization': f'Bearer {DJANGO_API_KEY}'}
            payload = {'token': token, 'chat_id': chat_id}
            response = requests.post(DJANGO_LINK_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            reply_message = response.json().get('message', "✅ Conta vinculada com sucesso!")

        elif text.startswith('/nota '):
            note_content = text.replace('/nota ', '', 1).strip()
            headers = {'Authorization': f'Bearer {DJANGO_API_KEY}'}
            payload = {'chat_id': chat_id, 'content': note_content}
            response = requests.post(DJANGO_NOTE_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            reply_message = response.json().get('message', "✅ Nota salva!")
        
        # --- NOVA LÓGICA DE DESVINCULAÇÃO ---
        elif text == '/desvincular':
            reply_message = "⚠️ Você tem certeza que deseja desvincular sua conta? Você não poderá mais adicionar notas pelo Telegram. Para confirmar, envie o comando: /desvincular sim"

        elif text == '/desvincular sim':
            headers = {'Authorization': f'Bearer {DJANGO_API_KEY}'}
            payload = {'chat_id': chat_id}
            response = requests.post(DJANGO_UNLINK_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            reply_message = response.json().get('message', "✅ Conta desvinculada com sucesso.")
            
        else:
            reply_message = "Comando não reconhecido. Use /vincular, /desvincular ou /nota."

    except Exception as e:
        reply_message = f"❌ Ocorreu um erro: {str(e)}"
        print(f"[ERROR] {str(e)}")

    # Envia a resposta final para o usuário
    requests.post(TELEGRAM_API_URL, json={'chat_id': chat_id, 'text': reply_message})
    
    return {'statusCode': 200}