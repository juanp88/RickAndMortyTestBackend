import json
import boto3

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
        character_id = body.get('characterId')  # Get the characterId
        character_name = body.get('name')  # Get the updated name (if provided)
        species = body.get('species')  # Get the updated species (if provided)
        status = body.get('status')  # Get the updated status (if provided)

        # Ensure characterId is provided
        if not character_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'characterId is required'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Initialize the update expression, attribute names, and values
        update_expression = "SET"
        expression_attribute_names = {}
        expression_attribute_values = {}

        if character_name:
            update_expression += " #name = :name,"
            expression_attribute_names["#name"] = "characterName"
            expression_attribute_values[":name"] = character_name

        if species:
            update_expression += " species = :species,"
            expression_attribute_values[":species"] = species

        if status:
            update_expression += " #status = :status,"
            expression_attribute_names["#status"] = "status"
            expression_attribute_values[":status"] = status

        # Remove trailing comma from the update expression
        if update_expression.endswith(","):
            update_expression = update_expression[:-1]

        # Execute the update in DynamoDB
        response = table.update_item(
            Key={
                'characterId': character_id  # Use characterId as the partition key
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"  # Return the updated item
        )

        # Get the updated item from the response
        updated_item = response.get('Attributes', {})

        # If no item was found with that characterId
        if not updated_item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Character not found'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Return the updated character
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Character updated successfully',
                'updatedCharacter': updated_item
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