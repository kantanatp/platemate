
from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from PIL import Image
from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

import io
import requests
app = Flask(__name__)

# app.config['SECRET_KEY'] = 'your_secret_key_here'

model_pipeline = pipeline(task="image-classification", model="nateraw/food")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        image = Image.open(io.BytesIO(file.read()))

        predictions = model_pipeline(images=image, top_k=3)
        
        if predictions:
            identified_dish_raw = predictions[0]['label']
            identified_dish = ' '.join(word.capitalize() for word in identified_dish_raw.split('_'))
            
            search_query = f"{identified_dish} recipe"
            google_search_url = f"https://www.google.com/search?q={search_query}"
            response = requests.get(google_search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Limiting to the top 100 search results
            search_results = soup.find_all('a')[:100]
            recipe_urls = [result.get('href') for result in search_results if 'url?q=' in result.get('href')]

            ingredients_lists = []  # List to store ingredients from different sources
            
            # Try scraping up to 5 supported URLs
            for recipe_url in recipe_urls[:5]:
                parsed_url = urlparse(recipe_url)
                actual_url = parse_qs(parsed_url.query).get('q')
                
                if actual_url and actual_url[0]:
                    actual_url = actual_url[0]
                    try:
                        scraper = scrape_me(actual_url)
                        ingredients = scraper.ingredients()
                        ingredients_lists.append({actual_url: ingredients})
                        if len(ingredients_lists) >= 5:
                            break
                    except WebsiteNotImplementedError:
                        continue
            
            return jsonify({'dish': identified_dish, 'ingredients_lists': ingredients_lists})
        else:
            return jsonify({'error': 'No dish recognized'})
    
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)