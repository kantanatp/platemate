from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = ''       # paste secret key

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
        # process image
        # send to google cloud vision API
        # placeholder response
        
        identified_dish = ""    # placeholder response
        
        recipes = ["recipe1", "recipe2", "recipe3"]    # placeholder response
        
        return jsonify({'dish': identified_dish, 'recipes': recipes})
    
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)