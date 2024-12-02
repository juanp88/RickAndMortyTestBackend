import urllib3
import json

def lambda_handler(event, context):
    # Parse query parameters
    page = event.get('queryStringParameters', {}).get('page', '1')

    # Fetch characters from Rick and Morty API
    rm_api_url = f"https://rickandmortyapi.com/api/character/?page={page}"
    http = urllib3.PoolManager()
    rm_response = http.request('GET', rm_api_url)
    rm_data = json.loads(rm_response.data.decode('utf-8'))

    result = {
        'api_characters': rm_data.get('results', [])
    }

    return rm_data
    ''' 
    {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    '''