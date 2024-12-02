import boto3
import uuid
import json

def lambda_handler(event, context):
    try:
        print("Event received:", json.dumps(event))  # Log the input event
        s3 = boto3.client('s3')
        bucket_name = 'new-characters-images'

        file_name = event.get('queryStringParameters', {}).get('fileName', f"{uuid.uuid4()}.jpg")
        print("File name:", file_name)  # Log the file name

        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': file_name, 'ContentType': 'image/jpeg'},
            ExpiresIn=300
        )
        print("Presigned URL generated:", presigned_url)  # Log the presigned URL

        return {
            'statusCode': 200,
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'fileUrl': f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            }),
            'headers': {
                'Content-Type': 'application/json'
            }  # Make sure this closing brace is present
        }
    except Exception as e:
        print("Error occurred:", str(e))  # Log the error
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'}),
            'headers': {
                'Content-Type': 'application/json'
            }  # Ensure this closing brace is present as well
        }