# lambda_function.py
import json
import os
import requests # Esta biblioteca precisa ser adicionada como um Layer

# Carrega as variáveis de ambiente
BOT_TOKEN = os.environ['BOT_TOKEN']
DJANGO_API_URL = os.environ['DJANGO_API_URL']
DJANGO_API_KEY = os.environ['DJANGO_API_KEY']
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def lambda_handler(event, context):
    try:
        # 1. Pega a mensagem do Telegram
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()

        # 2. Verifica se é um comando válido
        if not chat_id or not text.startswith('/nota '):
            return {'statusCode': 200}

        note_content = text.replace('/nota ', '', 1).strip()
        
        # 3. Prepara e envia os dados para a API do Django
        headers = {'Authorization': f'Bearer {DJANGO_API_KEY}'}
        # ATENÇÃO: Para este exemplo, estamos salvando a nota para o usuário com ID=1.
        # Uma implementação real teria um sistema para mapear o chat_id do Telegram ao usuário Django.
        payload = {'user_id': 1, 'content': note_content}
        
        response = requests.post(DJANGO_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status() # Lança um erro se a API do Django retornar erro

        reply_message = f"✅ Nota salva com sucesso!"

    except Exception as e:
        reply_message = f"❌ Erro ao salvar a nota: {str(e)}"

    # 4. Envia a resposta de volta ao usuário no Telegram
    requests.post(TELEGRAM_API_URL, json={'chat_id': chat_id, 'text': reply_message})
    
    return {'statusCode': 200}