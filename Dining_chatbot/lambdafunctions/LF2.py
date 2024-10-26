import json
import boto3
import json
import random
import requests
import os
import traceback
import re

from re import S

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
restaurauntTable = dynamodb.Table('yelp-restaurants')
userTable = dynamodb.Table('user-state')


class SQSQueue(object):
    def __init__(self, queue_url, region_name="us-east-1"):
        self.sqs = boto3.client("sqs", region_name=region_name)
        # self.queues = self.sqs.list_queues(QueueNamePrefix=queue_name)
        self.queue = queue_url

    def enqueue_message(self, msg):
        self.sqs.send_message(QueueUrl=self.queue, MessageBody=msg)

    def dequeue_message(self, wait_time_seconds=20):
        messages = self.sqs.receive_message(QueueUrl=self.queue, MaxNumberOfMessages=1, WaitTimeSeconds=wait_time_seconds)
        print(messages)
        if "Messages" in messages:
            message = messages["Messages"][0]
            return message
        else:
            return None

    def delete_message(self, receipt_handle):
        try:
            self.sqs.delete_message(QueueUrl=self.queue, ReceiptHandle=receipt_handle)
            print("Message deleted. ReceiptHandle:", receipt_handle)
        except:
            print("Unable to delete message:", receipt_handle)

    def set_visibility_timeout(self, receipt_handle, t):
        # t in minutes
        self.sqs.change_message_visibility(
            QueueUrl=self.queue, ReceiptHandle=receipt_handle, VisibilityTimeout=t
        )
        
def format_recommendation(restaurant, idx):
    return f"""
    ------------------------------------------
    Recommendation {idx+1}:
    Name: {restaurant['name']}
    Cuisine: {restaurant['cuisine']}
    Address: {restaurant['address']}
    Rating: {restaurant.get('rating', 'N/A')}
    ------------------------------------------
    """

def query_dynamodb(restaurant_id):
    response = restaurauntTable.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('BusinessID').eq(restaurant_id)
    )
    items = response['Items']
    if items:
        restaurant = random.choice(items)
        return restaurant
    else:
        return None

def get_restaurant_recommendations(cuisine):
    '''
        This function queries ES with the cuisine and then fetches more data about the restaurant from dynamodb, formats it and returns upto 5 recommendations
    '''
    # list to store results
    recommendations = []
    
    # Define the elastic search query
    query = {
        "size": 5,
        "query": {
            "match": {
                "Cuisine": cuisine
            }
        }
    }

    es_host = os.environ['OS_URL']
    index = 'restaurants'
    url = f"{es_host}/{index}/_search"
    username = os.environ['OS_USERNAME']
    password = os.environ['OS_PASSWORD']
    headers = {
      'Content-Type': 'application/json'
    }
    # Make the GET request to Elasticsearch
    response = requests.get(url, auth=(username, password), headers=headers, data=json.dumps(query))

   
    if response.status_code == 200 and response.json()['hits']['total']['value'] > 0:
        # Parse the response
        result = response.json()
        hits = result['hits']['hits']
        for idx, hit in enumerate(hits):
            dynamo_result = query_dynamodb(hit['_source']['RestaurantID'])
            result = format_recommendation(query_dynamodb(hit['_source']['RestaurantID']), idx)
            if result:
                recommendations.append(result)
        
    else:
        print(f"Error querying Elasticsearch: {response.status_code}, {response.text}")
        result = format_recommendation(query_dynamodb(recommendation))
        if result:
            recommendations.append(result)
    
    return recommendations

def create_or_update_user_recommendation(user_id, recommendation):
    try:
        # Check if user already exists in DB
        response = userTable.get_item(
            Key={
                'userId': user_id
            }
        )
        
        if 'Item' in response:
            # Update recommendation for existing user
            update_response = userTable.update_item(
                Key={
                    'userId': user_id
                },
                UpdateExpression='SET recentRecommendation = :r',
                ExpressionAttributeValues={
                    ':r': recommendation
                },
                ReturnValues="UPDATED_NEW"
            )
            print("Update succeeded:")
            print(update_response)
        else:
            # Create a new entry with userId and recommendation
            put_response = userTable.put_item(
                Item={
                    'userId': user_id,
                    'recentRecommendation': recommendation
                }
            )
            print("New item created:")
            print(put_response)
        
        
    except ClientError as e:
        print("Error updating/creating item:")
        print(e.response['Error']['Message'])
        
    except Exception as e:
        print("Unexpected error:")
        print(str(e))
        
        
def lambda_handler(event, context):
    # TODO implement
    worker_queue = SQSQueue(os.environ['SQS_URL'], "us-east-1")
    result = worker_queue.dequeue_message()
    if result is None:
        print("No jobs found. Aborting...")
        return {
            'statusCode': 204,  # 204 since successful processing but no content
            'body': json.dumps({"message": "No jobs found"})
        }
    
    try:
        print("Found Job", type(result["Body"]), result["Body"])
        body = eval(result["Body"])
        user_email = body["Email"]
        user_id = body.get("userId")
        receipt_handle = result["ReceiptHandle"]
        cuisine = body['Cuisine']
        recommendations = get_restaurant_recommendations(cuisine)
        
        # storing one of the recommendations as the most recent one for the current user
        random_recommendation = random.choice(recommendations)
        random_recommendation = re.sub(r'-+|Recommendation \d+:\s*', '', random_recommendation)
        create_or_update_user_recommendation(user_id, random_recommendation)
        
        # formatting the recommendations to send to user via email
        recommendations_formatted = "\n".join(recommendations)
        print("Reccomendations: ", recommendations_formatted)
        
        ses = boto3.client('ses', region_name='us-east-1')
        ses.send_email(
            Source='sr7420@nyu.edu',
            Destination={
                'ToAddresses': ['sr7420@nyu.edu'],
            },
            Message={
                'Subject': {
                    'Data': 'Restaurant Recommendations',
                },
                'Body': {
                    'Text': {
                        'Data': recommendations_formatted,
                    },
                },
            },
        )
        
        # deleting the processed packet from the queue
        worker_queue.delete_message(receipt_handle)
        
        return {
            'statusCode': 200,
            'body': json.dumps(body)
        }

    
    except Exception as e:
        print("Error in processing packet: ", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps(body),
            'exception_traceback': traceback.format_exc()
        }
