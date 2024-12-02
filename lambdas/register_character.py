import json
import boto3
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('new_characters')  # Replace with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # Log the incoming event for debugging
        print("Received event:", json.dumps(event))

        # Ensure the 'body' field exists
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No body found in the request'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Parse the incoming JSON body
        body = json.loads(event['body'])  # This assumes the body is a stringified JSON
        characterName = body.get('name')  # Change 'name' to 'characterName'
        species = body.get('species')
        status = body.get('status')
        image= body.get('image')

        # Ensure required fields are provided
        if not characterName or not species or not status:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'name, species, and status are required fields'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Generate a unique ID for the new character
        character_id = str(uuid.uuid4())

        # Store the new character in DynamoDB
        table.put_item(
            Item={
                'characterId': character_id,
                'characterName': characterName,  # Use 'characterName' instead of 'name'
                'species': species,
                'status': status,
                'image': image
            },
            ConditionExpression="attribute_not_exists(characterName)"  # Prevent duplicate character names
        )

        # Return success response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Character registered successfully',
                'characterId': character_id
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
