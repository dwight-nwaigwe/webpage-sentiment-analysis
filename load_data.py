# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 09:00:25 2026

@author: dwight
"""

import io
import os
from PIL import Image


# Replace with your actual API key or rely on your GOOGLE_API_KEY environment variable
os.environ["GOOGLE_API_KEY"] = "your_API_key"

target_image_path = "C:/Users/dwight/github repositories/webpage-sentiment-analysis/notebook_screenshot.png"
map_path = "C:/Users/dwight/github repositories/webpage-sentiment-analysis//map.jpg"


def get_images():

    img = Image.open(target_image_path)
    map_img = Image.open(map_path)
    return [img,map_img]
