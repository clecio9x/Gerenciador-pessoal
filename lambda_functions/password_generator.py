import json
import random
import string
import secrets

def lambda_handler(event, context):
    try:
        # Pegar parâmetros da requisição
        body = json.loads(event.get('body', '{}'))
        length = body.get('length', 12)
        include_symbols = body.get('symbols', True)
        include_numbers = body.get('numbers', True)
        include_uppercase = body.get('uppercase', True)
        include_lowercase = body.get('lowercase', True)
        
        # Construir conjunto de caracteres
        chars = ""
        if include_lowercase:
            chars += string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_numbers:
            chars += string.digits
        if include_symbols:
            chars += "!@#$%&*+-=?"
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        # Gerar senha segura
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Calcular força da senha
        strength = calculate_password_strength(password)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'password': password,
                'length': length,
                'strength': strength,
                'timestamp': str(context.aws_request_id)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def calculate_password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%&*+-=?" for c in password):
        score += 1
    
    strength_levels = ["Muito Fraca", "Fraca", "Regular", "Boa", "Forte", "Muito Forte"]
    return strength_levels[min(score, 5)]