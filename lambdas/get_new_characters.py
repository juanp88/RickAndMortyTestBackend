import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('new_characters')  # Replace with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # Log the incoming event for debugging
        print("Received event:", json.dumps(event))

        # Perform a scan operation to retrieve all items from the table
        response = table.scan()

        # Retrieve the list of items (characters)
        characters = response.get('Items', [])

        # Transform the field names for each character
        transformed_characters = [
            {
                'stringId': character.get('characterId'),
                'name': character.get('characterName'),
                'image': character.get('image'),
                'species': character.get('species'),
                'status': character.get('status'),
            }
            for character in characters
        ]

        # Return the transformed characters
        return {
            'statusCode': 200,
            'body': json.dumps({'characters': transformed_characters}),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }