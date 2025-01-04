# Cloud Computing Projects Repository

This repository contains three distinct projects focusing on cloud computing, serverless architectures, and distributed systems.

## Assignment 1: Restaurant Chatbot (AWS)

A dining concierge chatbot leveraging AWS services to provide restaurant recommendations through natural language interaction.

### Features
- Natural language processing with Amazon Lex
- Serverless backend with AWS Lambda
- Restaurant data storage in DynamoDB
- Efficient search with ElasticSearch
- Message queuing with AWS SQS
- RESTful endpoints via API Gateway

### Core Components

1. Lambda Functions:
   - LF1: Message processor & Lex interaction
   - LF2: Restaurant search & recommendations

2. Data Storage:
   - DynamoDB Tables: User states & restaurant information
   - ElasticSearch: Restaurant indexing & search
   - SQS Queue: Recommendation request handling

### Setup Guide
1. AWS Resource Creation:
   ```
   - Create Lambda functions (LF1, LF2)
   - Set up DynamoDB tables
   - Configure ElasticSearch domain
   - Create SQS queue
   - Build Lex bot with intents
   ```
2. Deploy Lambda functions
3. Set up API Gateway endpoints
4. Configure IAM roles & permissions

## Assignment 2: Flask-MongoDB Application

A containerized Flask application with MongoDB backend, deployed on Kubernetes.

### Features
- REST API with Flask
- MongoDB database integration
- Kubernetes orchestration
- Load balancing
- Persistent storage
- Secure credential management

### Project Structure
```
project/
├── flask-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── kubernetes/
    ├── flask-app.yaml
    ├── mongodb-deployment.yaml
    └── mongodb-service.yaml
```

### Deployment Steps
1. Build Docker image:
   ```bash
   docker build -t your-registry/todo-flask-app:1.0.0 ./flask-app
   ```

2. Push to registry:
   ```bash
   docker push your-registry/todo-flask-app:1.0.0
   ```

3. Deploy on Kubernetes:
   ```bash
   kubectl apply -f kubernetes/
   ```

## Assignment 3: Smart Photo Album (AWS)

A serverless photo album application enabling natural language search capabilities.

### Features
- Natural language photo search
- Automatic image labeling (Rekognition)
- Elasticsearch for photo indexing
- Custom label support
- Serverless architecture
- S3-hosted frontend

### System Architecture

1. Storage:
   - S3 Bucket B1: Frontend hosting
   - S3 Bucket B2: Photo storage

2. Processing:
   - Lambda LF1: Photo indexing
   - Lambda LF2: Search handling
   - Lex: Natural language processing
   - Elasticsearch: Photo metadata search
   - API Gateway: REST API management

### Deployment Guide
1. Run CloudFormation template for infrastructure
2. Deploy frontend to S3
3. Configure CodePipeline
4. Set up API Gateway & Lex bot

## General Setup Requirements

### AWS Configuration
Create `credentials.json`:
```json
{
  "aws_access_key_id": "YOUR_KEY",
  "aws_secret_access_key": "YOUR_SECRET",
  "region": "us-east-1"
}
```

### Environment Setup
Required environment variables:
```bash
AWS_REGION=us-east-1
ELASTICSEARCH_HOST=your-es-endpoint
LEX_BOT_ID=your-bot-id
SQS_QUEUE_URL=your-queue-url
```

## License
MIT License - See LICENSE file for details
