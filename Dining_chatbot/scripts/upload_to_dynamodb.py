import json
import subprocess
import os
from datetime import datetime

def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def format_for_dynamodb(item):
    # Convert Yelp data to DynamoDB format with required fields
    return {
        "PutRequest": {
            "Item": {
                "BusinessID": {"S": item["id"]},
                "name": {"S": item["name"]},
                "address": {"S": ", ".join(item["location"]["display_address"])},
                "latitude": {"N": str(item["coordinates"]["latitude"])},
                "longitude": {"N": str(item["coordinates"]["longitude"])},
                "review_count": {"N": str(item["review_count"])},
                "rating": {"N": str(item["rating"])},
                "zip_code": {"S": item["location"]["zip_code"]},
                "insertedAtTimestamp": {"S": datetime.now().isoformat()},
                "cuisine": {"S": item["Cuisine"]}
            }
        }
    }

# Load the JSON file
with open("restaurants_data_dynamodb.json", "r") as f:
    data = json.load(f)

# Get the items and format them for DynamoDB
items = [format_for_dynamodb(item) for item in data["Items"]]

# Split items into chunks of 25 (DynamoDB batch write limit)
chunked_items = chunk_list(items, 25)

# Your DynamoDB table name
table_name = "yelp-restaurants"

# Process each chunk
for i, chunk in enumerate(chunked_items):
    # Create a temporary JSON file for this chunk
    temp_filename = f"temp_chunk_{i}.json"
    with open(temp_filename, "w") as f:
        json.dump({table_name: chunk}, f)
    
    # Use AWS CLI to upload the chunk
    subprocess.run(["aws", "dynamodb", "batch-write-item", "--request-items", f"file://{temp_filename}"])
    
    # Remove the temporary file
    os.remove(temp_filename)

print("Data upload complete!")