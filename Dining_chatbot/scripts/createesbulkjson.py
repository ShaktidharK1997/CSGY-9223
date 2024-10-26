import json 

def create_es_bulk_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    new_bulk_data = []
    for item in data.get('Items', []):  # Use .get() to safely access 'Items' key
        action = {
            "index": {
                "_index": "restaurants",
                "_id": item["id"]
            }
        }

        new_bulk_data.append(json.dumps(action))

        document = {
            "RestaurantID": item["id"],  # Changed from BusinessID to RestaurantID
            "Cuisine": item["Cuisine"]
        }

        new_bulk_data.append(json.dumps(document))
        
    # Add a newline at the end of the file
    new_bulk_data.append("")

    with open("restaurants_bulk_data.json", "w") as f:
        f.write("\n".join(new_bulk_data))

if __name__ == "__main__":
    create_es_bulk_json("restaurants_data_dynamodb.json")
