from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from PIL import Image
import io
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key_here'

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
            identified_dish = predictions[0]['label']
            score = predictions[0]['score']

            recipes = ["recipe1", "recipe2", "recipe3"]
            
            return jsonify({'dish': identified_dish, 'score': score, 'recipes': recipes})
        else:
            return jsonify({'error': 'No dish recognized'})
    
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)
