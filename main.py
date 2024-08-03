# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 22:01:32 2024

@author: hp5cd
"""

import discord
import os
import asyncio
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

import welcome
from updateuser import update_user  # Import the update_user function

# MongoDB setup
def setup_mongodb():
    username = quote_plus("----")  # Replace with your actual username
    password = quote_plus("----")  # Replace with your actual password
    uri = f"mongodb+srv://{username}:{password}@discordbot-aic.easdzbj.mongodb.net/?retryWrites=true&w=majority&appName=DiscordBot-AIC"

    mongo_client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return mongo_client
    except Exception as e:
        print(f"Failed to connect to MongoDB. Error: {e}")
        return None

# Function to get commands from MongoDB
def get_commands_from_mongodb(mongo_client, database_name, collection_name):
    try:
        db = mongo_client[database_name]
        collection = db[collection_name]
        commands = list(collection.find())
        print("Retrieved documents:")
        for doc in commands:
            print(doc)
        command_responses = {doc['command']: doc['response'] for doc in commands}
        print(f"Successfully fetched commands from MongoDB database '{database_name}', collection '{collection_name}'")
        return command_responses
    except Exception as e:
        print(f"Error fetching commands from MongoDB: {e}")
        return {}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # This is crucial for receiving member join events
discord_client = discord.Client(intents=intents)

# We'll populate this dictionary from MongoDB
command_responses = {}

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')

@discord_client.event
async def on_member_join(member):
    try:
        channel = member.guild.system_channel  # Or specify a channel ID
        if channel is not None:
            avatar_url = str(member.avatar.url) if member.avatar else str(member.default_avatar.url)
            img_buffer = welcome.image(member.name, avatar_url, "welcome.png")  # Make sure this function name matches your welcome.py file
            file = discord.File(fp=img_buffer, filename='welcome.png')
            await channel.send(f'{member.mention}!', file=file)
            print(f'New member joined: {member.name}')
        else:
            print(f"No system channel found for guild: {member.guild.name}")
    except Exception as e:
        print(f"Error in on_member_join: {e}")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return
    username = message.author.name
    message_type = "Unknown"

    if message.content:
        message_type = "text"
    elif message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image'):
                message_type = "image"
            elif attachment.content_type.startswith('video'):
                message_type = "video"
            elif attachment.content_type.startswith('audio'):
                message_type = "audio"
    
    msg, upd_usr = update_user(mongo_client, username, message_type)
    if msg:
        await message.channel.send(msg)
    
    if message.content.startswith('$'):
        full_command = message.content[1:].split()
        command = full_command[0].lower()
        
        if command in command_responses:
            response = command_responses[command]
            await message.channel.send(response)
        else:
            await message.channel.send(f"Sorry, I don't recognize the command '${command}'. Type '$help' for a list of available commands.")

async def main():
    global command_responses, mongo_client
    
    # Setup MongoDB
    mongo_client = setup_mongodb()
    if mongo_client is None:
        print("Failed to setup MongoDB. Exiting.")
        return

    # Specify your database and collection names here
    database_name = "DiscordBot"
    collection_name = "DiscordBot-AIC"

    # Fetch commands from MongoDB
    command_responses = get_commands_from_mongodb(mongo_client, database_name, collection_name)

    # Start Discord bot
    token = os.getenv('DISCORD_TOKEN')
    if token is None:
        raise ValueError("No DISCORD_TOKEN found in environment variables")
    
    await discord_client.start(token)

if __name__ == "__main__":
    asyncio.run(main())
