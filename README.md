# Rick and Morty Test Backend

AWS Lambda backend services for the Rick and Morty Test Flutter application. This backend provides serverless API endpoints for character upload functionality using AWS Lambda, API Gateway, and S3.

## Overview

This backend provides:
- AWS Lambda functions for handling character image uploads
- API Gateway endpoints for the Flutter app
- S3 bucket configuration for image storage
- Serverless architecture for scalability and cost-effectiveness

## Architecture

```
Backend/
├── src/
│   ├── handlers/
│   │   ├── upload-handler.js      # Main upload Lambda function
│   │   ├── list-characters.js     # List uploaded characters
│   │   └── get-character.js       # Retrieve specific character
│   ├── utils/
│   │   ├── s3-client.js           # S3 configuration
│   │   ├── response-helper.js     # API response formatting
│   │   └── validation.js          # Input validation utilities
│   └── config/
│       └── aws-config.js          # AWS configuration
├── serverless.yml                 # Serverless Framework configuration
├── package.json
├── .env.example                   # Environment variables template
└── README.md
```

## Prerequisites

- Node.js 18.x or higher
- AWS CLI configured with appropriate permissions
- Serverless Framework CLI (`npm install -g serverless`)
- AWS account with admin access or specific IAM permissions

## AWS Services Required

- **AWS Lambda** - Serverless compute
- **Amazon S3** - Image storage
- **Amazon API Gateway** - REST API endpoints
- **AWS IAM** - Permissions and roles
- **Amazon CloudWatch** - Logging and monitoring

## Setup Instructions

### 1. Clone and Install

```bash
git clone [backend-repo-url] D:\Flutter\RickAndMortyTestBackend
cd D:\Flutter\RickAndMortyTestBackend
npm install
```

### 2. AWS Configuration

#### Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your preferred region (e.g., us-east-1)
```

#### Create IAM Role for Lambda
Create a file `iam-role.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the role:
```bash
aws iam create-role \
  --role-name rickandmorty-lambda-role \
  --assume-role-policy-document file://iam-role.json

aws iam attach-role-policy \
  --role-name rickandmorty-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name rickandmorty-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 3. Environment Configuration

#### Create .env file
Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

**File: `.env`**
```
AWS_REGION=us-east-1
S3_BUCKET_NAME=rickandmorty-character-images-[unique-id]
API_STAGE=dev
LAMBDA_ROLE_ARN=arn:aws:iam::[your-account-id]:role/rickandmorty-lambda-role
```

#### Create .env.example
```bash
# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET_NAME=rickandmorty-character-images-[your-unique-id]
API_STAGE=dev
LAMBDA_ROLE_ARN=arn:aws:iam::[your-account-id]:role/rickandmorty-lambda-role

# Optional: CORS settings
ALLOWED_ORIGINS=https://your-flutter-app-domain.com
```

### 4. S3 Bucket Setup

Create the S3 bucket for image storage:

```bash
# Create bucket
aws s3 mb s3://rickandmorty-character-images-[unique-id] --region us-east-1

# Configure CORS for bucket
echo '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": []
    }
  ]
}' > cors-config.json

aws s3api put-bucket-cors --bucket rickandmorty-character-images-[unique-id] --cors-configuration file://cors-config.json
```

### 5. Deploy with Serverless Framework

#### Install Serverless Framework
```bash
npm install -g serverless
```

#### Deploy All Services
```bash
serverless deploy --stage dev --verbose
```

#### Deploy Individual Functions
```bash
# Deploy specific function
serverless deploy function --function uploadHandler --stage dev
```

### 6. Manual Deployment (Alternative)

If not using Serverless Framework, deploy manually:

#### Package Lambda Functions
```bash
# Package each function
zip -r upload-handler.zip src/handlers/upload-handler.js src/utils/
zip -r list-characters.zip src/handlers/list-characters.js src/utils/
zip -r get-character.zip src/handlers/get-character.js src/utils/
```

#### Create Lambda Functions
```bash
# Upload handler
aws lambda create-function \
  --function-name rickandmorty-upload-handler \
  --runtime nodejs18.x \
  --role arn:aws:iam::[account-id]:role/rickandmorty-lambda-role \
  --handler src/handlers/upload-handler.handler \
  --zip-file fileb://upload-handler.zip \
  --environment Variables={BUCKET_NAME=rickandmorty-character-images-[unique-id],REGION=us-east-1} \
  --timeout 30

# List characters
aws lambda create-function \
  --function-name rickandmorty-list-characters \
  --runtime nodejs18.x \
  --role arn:aws:iam::[account-id]:role/rickandmorty-lambda-role \
  --handler src/handlers/list-characters.handler \
  --zip-file fileb://list-characters.zip \
  --environment Variables={BUCKET_NAME=rickandmorty-character-images-[unique-id],REGION=us-east-1}

# Get character
aws lambda create-function \
  --function-name rickandmorty-get-character \
  --runtime nodejs18.x \
  --role arn:aws:iam::[account-id]:role/rickandmorty-lambda-role \
  --handler src/handlers/get-character.handler \
  --zip-file fileb://get-character.zip \
  --environment Variables={BUCKET_NAME=rickandmorty-character-images-[unique-id],REGION=us-east-1}
```

### 7. API Gateway Setup

#### Create REST API
```bash
# Create API
aws apigateway create-rest-api --name 'RickAndMortyAPI' --description 'API for Rick and Morty character uploads'
```

#### Get API ID and create resources
```bash
# Get API ID
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`RickAndMortyAPI`].id' --output text)

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create /upload resource
UPLOAD_RESOURCE=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part upload --query 'id' --output text)

# Create /characters resource
CHARACTERS_RESOURCE=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part characters --query 'id' --output text)

# Create /characters/{id} resource
CHARACTER_ID_RESOURCE=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $CHARACTERS_RESOURCE --path-part {id} --query 'id' --output text)
```

#### Create Methods and Integrations
```bash
# POST /upload
aws apigateway put-method --rest-api-id $API_ID --resource-id $UPLOAD_RESOURCE --http-method POST --authorization-type NONE
aws apigateway put-integration --rest-api-id $API_ID --resource-id $UPLOAD_RESOURCE --http-method POST --type AWS_PROXY --integration-http-method POST --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:[account-id]:function:rickandmorty-upload-handler/invocations

# GET /characters
aws apigateway put-method --rest-api-id $API_ID --resource-id $CHARACTERS_RESOURCE --http-method GET --authorization-type NONE
aws apigateway put-integration --rest-api-id $API_ID --resource-id $CHARACTERS_RESOURCE --http-method GET --type AWS_PROXY --integration-http-method POST --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:[account-id]:function:rickandmorty-list-characters/invocations

# GET /characters/{id}
aws apigateway put-method --rest-api-id $API_ID --resource-id $CHARACTER_ID_RESOURCE --http-method GET --authorization-type NONE
aws apigateway put-integration --rest-api-id $API_ID --resource-id $CHARACTER_ID_RESOURCE --http-method GET --type AWS_PROXY --integration-http-method POST --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:[account-id]:function:rickandmorty-get-character/invocations
```

#### Deploy API
```bash
# Create deployment
aws apigateway create-deployment --rest-api-id $API_ID --stage-name dev --stage-description 'Development stage'
```

#### Configure CORS
```bash
# Enable CORS for all endpoints
echo '{
  "AllowMethods": ["GET", "POST", "OPTIONS"],
  "AllowHeaders": ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
  "AllowOrigins": ["*"]
}' > cors.json

aws apigateway put-method --rest-api-id $API_ID --resource-id $UPLOAD_RESOURCE --http-method OPTIONS --authorization-type NONE
aws apigateway put-method-response --rest-api-id $API_ID --resource-id $UPLOAD_RESOURCE --http-method OPTIONS --status-code 200
```

## API Endpoints

After deployment, your API will have the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `https://[api-id].execute-api.[region].amazonaws.com/dev/upload` | Upload character image |
| GET | `https://[api-id].execute-api.[region].amazonaws.com/dev/characters` | List uploaded characters |
| GET | `https://[api-id].execute-api.[region].amazonaws.com/dev/characters/{id}` | Get specific character |

## Testing

### Test Lambda Functions Locally
```bash
# Install SAM CLI
npm install -g aws-sam-cli

# Test upload handler
sam local invoke -e test-events/upload-event.json rickandmorty-upload-handler
```

### Test API Endpoints
```bash
# Test upload endpoint
curl -X POST \
  https://[api-id].execute-api.[region].amazonaws.com/dev/upload \
  -H 'Content-Type: application/json' \
  -d '{"name": "Test Character", "image": "base64-encoded-image", "species": "Human"}'

# Test list endpoint
curl https://[api-id].execute-api.[region].amazonaws.com/dev/characters

# Test get character
curl https://[api-id].execute-api.[region].amazonaws.com/dev/characters/character-id
```

## Monitoring and Logging

### View CloudWatch Logs
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/rickandmorty-

# Tail specific function logs
aws logs tail /aws/lambda/rickandmorty-upload-handler --follow
```

### Set Up Alarms
```bash
# Create CloudWatch alarm for errors
aws cloudwatch put-metric-alarm \
  --alarm-name rickandmorty-lambda-errors \
  --alarm-description "Alert on Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

## Security Best Practices

1. **IAM Roles**: Use least-privilege IAM roles for Lambda functions
2. **S3 Bucket Policy**: Restrict bucket access to specific Lambda functions
3. **API Gateway**: Use API keys or IAM authentication for production
4. **Environment Variables**: Never commit sensitive data to version control
5. **CORS**: Configure specific allowed origins instead of wildcard (*)

## Cleanup

To remove all AWS resources:

```bash
# Delete Lambda functions
aws lambda delete-function --function-name rickandmorty-upload-handler
aws lambda delete-function --function-name rickandmorty-list-characters
aws lambda delete-function --function-name rickandmorty-get-character

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id [api-id]

# Delete S3 bucket (empty first)
aws s3 rm s3://rickandmorty-character-images-[unique-id] --recursive
aws s3 rb s3://rickandmorty-character-images-[unique-id]

# Delete IAM role (detach policies first)
aws iam detach-role-policy --role-name rickandmorty-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name rickandmorty-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam delete-role --role-name rickandmorty-lambda-role
```

## Troubleshooting

### Common Issues

1. **Lambda timeout**: Increase timeout in function configuration
2. **S3 access denied**: Check IAM role permissions and bucket policy
3. **CORS errors**: Verify API Gateway CORS configuration
4. **Large image uploads**: Increase Lambda memory and timeout settings

### Debug Commands
```bash
# Check Lambda configuration
aws lambda get-function --function-name rickandmorty-upload-handler

# Test S3 access
aws s3 ls s3://rickandmorty-character-images-[unique-id]

# Check API Gateway configuration
aws apigateway get-resources --rest-api-id [api-id]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues with AWS deployment or configuration, please:
1. Check CloudWatch logs for detailed error messages
2. Verify all environment variables are correctly set
3. Ensure IAM roles have necessary permissions
4. Check the troubleshooting section above

## License

This backend service is provided as-is for testing purposes. Ensure you comply with AWS terms of service and best practices for production deployments.