import json
import random
import string

def lambda_handler(event, context):
    length = event.get('length', 12)
    include_symbols = event.get('symbols', True)
    
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'password': password,
            'length': length
        })
    }