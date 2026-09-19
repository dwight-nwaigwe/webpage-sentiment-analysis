# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 07:18:11 2026

@author: dwight
"""

import io
from google import genai
from google.genai import types
from PIL import Image
# 1. Initialize the client (ensure GEMINI_API_KEY env var is set)
client = genai.Client()


def my_gemini_function(img, map_img):
    
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[img,
            """Look at this image which is a screenshot of a website. Spend time understanding the layout, including which subimages belong to which text."""
        ],
    )
    
    response = client.models.generate_content(
         model="gemini-2.5-flash-image",
         contents=[img,
             """Now that you have thought about the image I gave you, I want you to identify what the topics or stories are. 
             For each topic, determine the country and the sentiment
             associated with the topic. Rank the sentiment on a scale of 1-10, with 1 being the worst sentiment
             and 10 being the best. Return your answer as list of (country, score). Do not output the sentiment.
             Here is example output: 
                 "(Sweden, 7)\n*   (Uganda, 4)\n*   (Yemen, 2)\n*   (Saudi Arabia, 2)\n*   
                 (Yemen, 2)\n*   (India, 3)\n*   (Iran, 4)\n*   (Yemen, 2)\n*   (Djibouti, 3)\n*   (India, 3)\n*   (Iran, 4)\n*   (Manchester, 5)\n*   (Saudi Arabia, 2)\n*   (Palestine, 2)\n*   (Yemen, 2)\n*   (Palestine, 3)\n*   (Sweden, 6)\n*   (Palestine, 3)\n*   (Yemen, 2)\n*   (India, 3)\n*   (Yemen, 2)\n*   (Sweden, 7)\n*   (Yemen, 2)\n*   (Poland, 3)\n*   (Saudi Arabia, 2)\n*   (India, 3)\n*   (Yemen, 2)\n*   (India, 2)\n*   (Yemen, 3)\n*   (Barcelona, 8)"
             """
         ],
     )       
        
        
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[
            map_img,
            f"""Use the list of (country, score) that you made to fill in the map provided, shading each country
            based on score. Red for the lowest score, and green for the highest, and a shade scale for numbers between the 
            lowest and highest.Make sure you use the map provided, and only return an image in your response. Here are the
            countires and scores I want you to use: {response.text}""",
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    
    
    # 3. Extract and display the modified image
    candidate = response.candidates[0]
    
    # Check if the model generated image parts
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            if part.inline_data:
                # Convert response bytes to a PIL Image
                image_bytes = part.inline_data.data
                modified_image = Image.open(io.BytesIO(image_bytes))
                
                modified_image.save("gemini_modified_output.png")
                print("Successfully saved modified image as gemini_modified_output.png")
    else:
        print(f"A map was not made by the LLM. Official error: {candidate.finish_reason}")
    return modified_image