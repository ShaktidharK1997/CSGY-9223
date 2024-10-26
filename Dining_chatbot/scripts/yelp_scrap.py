import requests
import json
import time
from collections import defaultdict

# Your Yelp API key
API_KEY = "******"

# Yelp Fusion API endpoint
ENDPOINT = "https://api.yelp.com/v3/businesses/search"

# Headers for API request
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def get_restaurants(cuisine, offset=0):
    params = {
        "term": f"{cuisine} restaurants",
        "location": "Manhattan, NY",
        "limit": 50,
        "offset": offset
    }
    
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return response.json()


def collect_restaurants():
    CUISINES = ["Chinese", "Italian", "Mexican"]
    
    total_restaurants = []
    
    for cuisine in CUISINES:
        offset = 0
        cuisine_count = 0
        
        while cuisine_count < 150:
            restaurants_for_cuisine = get_restaurants(cuisine, offset)
            
            if "businesses" not in restaurants_for_cuisine:
                print(f"Restaurants over for {cuisine}, only {cuisine_count} found")
                break
            
            for business in restaurants_for_cuisine['businesses']:
                business['Cuisine'] = cuisine
                total_restaurants.append(business)
            
            cuisine_count += len(restaurants_for_cuisine['businesses'])
            
            offset += 50
            time.sleep(1)  # To prevent rate limiting
    
    return total_restaurants

if __name__ == "__main__":
    restaurants = collect_restaurants()
    
    print(f"Total restaurants collected: {len(restaurants)}")
    
    with open("restaurants_data_dynamodb.json", "w") as f:
        json.dump({"Items": restaurants}, f, indent=2)
    
    print("Data saved to restaurants_data_dynamodb.json")
