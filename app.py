from flask import Flask, jsonify, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
from PIL import Image
from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from transformers import pipeline
from urllib.parse import parse_qs, urlparse

import io
import re
import requests

app = Flask(__name__)

model_pipeline = pipeline(task="image-classification", model="nateraw/food")

@app.route('/')
def index():
    # Render the landing page
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if file:
            image = Image.open(io.BytesIO(file.read()))

            # Assuming your model_pipeline logic here
            predictions = model_pipeline(images=image, top_k=3)
            dishes = [(prediction['label'].replace('_', ' ').title(), 24 - i*2) for i, prediction in enumerate(predictions)]

            return render_template('options.html', dishes=dishes)
    else:
        # For a GET request, just render the upload form
        return render_template('upload.html')

    return jsonify({'error': 'An error occurred'}), 500

@app.route('/recipe-sources/<dish>')
def recipe_sources(dish):
    search_query = f"{dish} recipe"
    google_search_url = f"https://www.google.com/search?q={search_query}"
    response = requests.get(google_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    search_results = soup.find_all('a')[:100]
    recipe_urls = [result.get('href') for result in search_results if 'url?q=' in result.get('href')]

    added_sites = set()
    matched_sites = []

    for recipe_url in recipe_urls[:5]:
        parsed_url = urlparse(recipe_url)
        actual_url = parse_qs(parsed_url.query).get('q')
        
        if actual_url and actual_url[0]:
            actual_url = actual_url[0]
            try:
                scraper = scrape_me(actual_url)
                site_name = scraper.host()
                clean_site_name = site_name.split('.')[-2].capitalize() if site_name.count('.') > 1 else site_name.capitalize()

                if all(clean_site_name != site[0] for site in matched_sites):
                    matched_sites.append((clean_site_name, actual_url))
                    added_sites.add(clean_site_name)  # Update this set if needed elsewhere
                    if len(matched_sites) >= 5:
                        break
            except WebsiteNotImplementedError:
                continue

    if not matched_sites:
        message = "Sorry, there are no recipes that match our database. Please try again."
        return render_template('no_matches.html', message=message)

    return render_template('recipe_sources.html', dish=dish, matched_sites=matched_sites)

def clean_ingredient(ingredient):
    # Standardize measurements and terms
    replacements = {
        'tbsp': 'tablespoons',
        'tsp': 'teaspoons',
        'g': 'grams',
        'oz': 'ounces'
    }

    for old, new in replacements.items():
        ingredient = re.sub(r'\b' + re.escape(old) + r'\b', new, ingredient)

    # Remove content within parentheses, but keep "optional"
    ingredient = re.sub(r'\((?!.*?optional).*?\)', '', ingredient, flags=re.IGNORECASE)
    ingredient = re.sub(r'\(optional[^\)]*\)', '(optional)', ingredient, flags=re.IGNORECASE)

    # Remove any trailing commas and spaces
    ingredient = ingredient.rstrip(', ')

    # Remove unpaired parentheses
    open_parentheses = ingredient.count('(')
    close_parentheses = ingredient.count(')')

    while open_parentheses != close_parentheses:
        if open_parentheses > close_parentheses:
            ingredient = ingredient.rpartition('(')[0] + ingredient.rpartition('(')[2]
            open_parentheses -= 1
        else:
            ingredient = ingredient.rpartition(')')[0] + ingredient.rpartition(')')[2]
            close_parentheses -= 1

    # Capitalize first letter and strip leading/trailing whitespace
    ingredient = ingredient.strip().capitalize()

    return ingredient

@app.route('/ingredients')
def ingredients():
    recipe_url = request.args.get('url')
    
    if recipe_url:
        try:
            scraper = scrape_me(recipe_url)
            raw_ingredients = scraper.ingredients()
            cleaned_ingredients = [clean_ingredient(ing) for ing in raw_ingredients]
        except WebsiteNotImplementedError:
            cleaned_ingredients = ["This website is not supported for ingredient extraction."]
    else:
        cleaned_ingredients = ["No recipe URL was provided."]

    return render_template('ingredients.html', ingredients=cleaned_ingredients, recipe_url=recipe_url)

@app.route('/sustainable-example')
def sustainable_example():
    recipe_url = request.args.get('url')
    storage_tips = ""
    if recipe_url == "https://www.recipetineats.com/carbonara/":
        storage_tips = {
            'title': 'Leftover Ingredients Storage Tips',
            'tips': [
                'guanciale: plastic wrapped in refrigerator',
                'eggs: stored in refrigerator at 40F',
                'parmigiano reggiano: plastic wrapped in refrigerator',
                'black pepper: store in airtight container',
                'spaghetti: store in cool, dry place',
                'salt: store in airtight container',
                'garlic: store in refrigerator'
            ],
            'leftovers': 'Store in airtight container in refrigerator for 3-5 days'
        }
    elif recipe_url == "https://tastesbetterfromscratch.com/pad-thai/":
        storage_tips = {
            'title': 'Leftover Ingredients Storage Tips',
            'tips': [
                'flat rice noodle: store in airtight container',
                'garlic: store in refrigerator',
                'shrimp: store in refrigerator, can be kept up to 3 days',
                'chicken: store in refrigerator, can be kept up to 3 days',
                'eggs: stored in refrigerator at 40F',
                'bean sprouts: cover with paper towel and store in refrigerator',
                'green onions: store in refrigerator',
                'lime: store in refrigerator',
                'fish sauce: store in cool, dark place',
                'soy sauce: store in cool, dark place'
            ],
            'leftovers': 'Store in airtight container in refrigerator for up to 3 days'
        }
    return render_template('sustainable(example).html', storage_tips=storage_tips, recipe_url=recipe_url)

if __name__ == '__main__':
    app.run(debug=True)



# from bs4 import BeautifulSoup
# from flask import Flask, jsonify, render_template, request
# from PIL import Image
# from recipe_scrapers import scrape_me, WebsiteNotImplementedError
# from transformers import pipeline
# from urllib.parse import parse_qs, urlparse

# import io
# import requests

# app = Flask(__name__)

# # app.config['SECRET_KEY'] = 'your_secret_key_here'

# model_pipeline = pipeline(task="image-classification", model="nateraw/food")

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image provided'}), 400
    
#     file = request.files['image']
    
#     if file.filename == '':
#         return jsonify({'error': 'No image selected'}), 400
    
#     if file:
#         image = Image.open(io.BytesIO(file.read()))

#         predictions = model_pipeline(images=image, top_k=3)
        
#         if predictions:
#             identified_dish_raw = predictions[0]['label']
#             identified_dish = ' '.join(word.capitalize() for word in identified_dish_raw.split('_'))
            
#             search_query = f"{identified_dish} recipe"
#             google_search_url = f"https://www.google.com/search?q={search_query}"
#             response = requests.get(google_search_url)
#             soup = BeautifulSoup(response.text, 'html.parser')
            
#             # Limiting to the top 100 search results
#             search_results = soup.find_all('a')[:100]
#             recipe_urls = [result.get('href') for result in search_results if 'url?q=' in result.get('href')]

#             ingredients_lists = []  # List to store ingredients from different sources
            
#             # Try scraping up to 5 supported URLs
#             for recipe_url in recipe_urls[:5]:
#                 parsed_url = urlparse(recipe_url)
#                 actual_url = parse_qs(parsed_url.query).get('q')
                
#                 if actual_url and actual_url[0]:
#                     actual_url = actual_url[0]
#                     try:
#                         scraper = scrape_me(actual_url)
#                         ingredients = scraper.ingredients()
#                         ingredients_lists.append({actual_url: ingredients})
#                         if len(ingredients_lists) >= 5:
#                             break
#                     except WebsiteNotImplementedError:
#                         continue
            
#             return jsonify({'dish': identified_dish, 'ingredients_lists': ingredients_lists})
#         else:
#             return jsonify({'error': 'No dish recognized'})
    
#     return jsonify({'error': 'Something went wrong'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)