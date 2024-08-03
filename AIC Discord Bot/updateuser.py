# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 22:01:32 2024

@author: hp5cd
"""

from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

def setup_mongodb():
    username = quote_plus("Ishaan")  # Replace with your actual username
    password = quote_plus("#D15C@aic")  # Replace with your actual password
    uri = f"mongodb+srv://{username}:{password}@discordbot-aic.easdzbj.mongodb.net/?retryWrites=true&w=majority&appName=DiscordBot-AIC"

    mongo_client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return mongo_client
    except Exception as e:
        print(f"Failed to connect to MongoDB. Error: {e}")
        return None

def update_user(mongo_client, username, media_type):
    if media_type not in ["text", "image", "audio", "video"]:
        raise ValueError("media_type must be one of 'text', 'image', 'audio', 'video'")
    
    db = mongo_client["DiscordBot"]
    collection = db["UserStats"]
    
    # Determine the score increment based on the media type
    score_increment = 0
    if media_type in ["text", "audio"]:
        score_increment = 5
    elif media_type == "image":
        score_increment = 10
    elif media_type == "video":
        score_increment = 15

    # Find the user document by username
    user = collection.find_one({"username": username})
    news = False
    
    if user:
        # Calculate new score
        new_score = user.get("score", 0) + score_increment
        level_increment = 0
        
        if new_score >= 100:
            level_increment = 1
            new_score = 0  # Reset score to 0
        
        # If the user exists, update the media_type field, score, and level if necessary
        update_fields = {
            "$inc": {
                media_type: 1,
                "level": level_increment
            },
            "$set": {
                "score": new_score
            }
        }
        
        updated_user = collection.find_one_and_update(
            {"username": username},
            update_fields,
            return_document=ReturnDocument.AFTER
        )
        
        if level_increment:
            news = f"User {username} has leveled up to {user.get('level', 0) + level_increment}!"
        
    else:
        # If the user does not exist, create a new document
        new_user = {
            "username": username,
            "score": score_increment,
            "level": 0,
            "text": 0,
            "image": 0,
            "audio": 0,
            "video": 0,
            media_type: 1  # Initialize the given media_type with 1
        }
        
        # Check if initial score causes level up
        if new_user["score"] >= 100:
            new_user["level"] += 1
            news = f"User {username} has leveled up to {new_user['level']}!"
            new_user["score"] = 0  # Reset score to 0
        
        collection.insert_one(new_user)
        updated_user = new_user

    return news, updated_user

# Example usage:
client = setup_mongodb()
updated_user, news = update_user(client, "Shhaiiishhh", "video")
print(updated_user)
if news:
    print(news)
