# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 16:05:44 2024

@author: hp5cd
"""

from PIL import Image, ImageDraw, ImageFont
import io
import requests
from io import BytesIO
import cv2
import numpy as np

def create_gradient_border(avatar_size, border_size, start_color, end_color):
    border_avatar_size = (avatar_size[0] + 2 * border_size, avatar_size[1] + 2 * border_size)
    gradient_border = Image.new("RGBA", border_avatar_size)
    draw = ImageDraw.Draw(gradient_border)
    
    for i in range(border_size):
        factor = i / border_size
        color = (
            int(start_color[0] + factor * (end_color[0] - start_color[0])),
            int(start_color[1] + factor * (end_color[1] - start_color[1])),
            int(start_color[2] + factor * (end_color[2] - start_color[2])),
            255
        )
        draw.ellipse(
            (
                i,
                i,
                border_avatar_size[0] - i,
                border_avatar_size[1] - i
            ),
            outline=color
        )
    
    return gradient_border

def image(username, avatar_url, save_path):
    print(avatar_url)
    # Open the background image
    background = Image.open(r"D:\Ishaan\Portfolio\public\homebg2.png").convert("RGBA")
    bg_width, bg_height = background.size
    print(bg_height, bg_width)
    
    # Download and open the user's avatar
    response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")
    
    # Calculate avatar size and position
    avatar_radius = bg_width // 10  # 1/10th of the width
    avatar_size = (avatar_radius * 2, avatar_radius * 2)
    avatar_position = (bg_width // 2 - avatar_radius, int(bg_height * 3 / 8) - avatar_radius)
    
    # Resize avatar and make it circular
    avatar = avatar.resize(avatar_size, Image.LANCZOS)
    mask = Image.new("L", avatar_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar_size, fill=255)
    avatar.putalpha(mask)
    
    # Create a gradient border for the avatar
    border_size = 10
    start_color = (0, 255, 0)  # Green
    end_color = (0, 0, 255)    # Blue
    gradient_border = create_gradient_border(avatar_size, border_size, start_color, end_color)
    
    # Paste the avatar onto the gradient border
    gradient_border.paste(avatar, (border_size, border_size), avatar)
    
    # Paste the bordered avatar onto the background
    background.paste(gradient_border, (avatar_position[0] - border_size, avatar_position[1] - border_size), gradient_border)
    
    draw = ImageDraw.Draw(background)
    
    # Add "WELCOME" text
    welcome_font = ImageFont.truetype(r"D:\Ishaan\Portfolio\public\Comfortaa-VariableFont_wght.ttf", bg_height*bg_width*150//2985984)
    draw.text((background.width // 2, int(2.6 * bg_height // 4)), "WELCOME", font=welcome_font, fill="white", anchor="mm")
    
    # Add username
    username_font = ImageFont.truetype(r"D:\Ishaan\Portfolio\public\Comfortaa-VariableFont_wght.ttf", bg_height*bg_width*85//2985984)
    draw.text((background.width // 2, int(3.0 * bg_height // 4)), username, font=username_font, fill="#00FF00", anchor="mm")
    
    # Add welcome message
    message_font = ImageFont.truetype(r"D:\Ishaan\Portfolio\public\Comfortaa-VariableFont_wght.ttf", bg_height*bg_width*60//2985984)
    message = "Dive into the flow of conversations and connections!!"
    draw.text((background.width // 2, int(3.4 * bg_height // 4)), message, font=message_font, fill="white", anchor="mm", align="center")
    
    # Convert the PIL image to a format suitable for OpenCV
    open_cv_image = cv2.cvtColor(np.array(background), cv2.COLOR_RGBA2BGRA)
    
    # Save the image using OpenCV
    #cv2.imwrite(save_path, open_cv_image)
    
    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    background.save(buffer, 'PNG')
    buffer.seek(0)
    
    return buffer

# Example usage
#image("kamehameha", "https://cdn.discordapp.com/avatars/871335231020486676/4d7e604a8dddf4041ce0b476c50066d1.png?size=1024", "D:\Ishaan\Bin Arena\AIC Discord Bot\welcome_image.png")
