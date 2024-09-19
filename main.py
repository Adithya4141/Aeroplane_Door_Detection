from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
import cv2
import numpy as np
import os
import datetime
import sqlite3

# Class labels for prediction
classes = ["close", "open"]

# Initialize Flask app
app = Flask(__name__)

# Load YOLOv8 model (you can use your trained model's path)
model = YOLO("models/best.pt")  # Use the correct model path

# Route to load home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image uploads and predictions
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file:
        # Save file to disk
        image_path = os.path.join("static", file.filename)
        file.save(image_path)

        # Read image
        img = cv2.imread(image_path)

        # Run YOLOv8 inference
        results = model(img)
        for det in results[0].boxes:
            class_index = int(det.cls[0])  # Get the class index
            a = results[0].names[class_index]

        # Process results (bounding boxes, labels, etc.)
        annotated_img = results[0].plot()

        # Save the annotated image
        result_path = os.path.join("static", "result.jpg")
        cv2.imwrite(result_path, annotated_img)

        # Insert the prediction result into the database
        now = datetime.datetime.now()
        object_count = len(results[0].boxes)  # Object count
        
        # Connect to SQLite database
        conn = sqlite3.connect('aeroplane_door_open_data.db')
        cur = conn.cursor()
        
        # Create users table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                class TEXT NOT NULL,
                no INTEGER,
                Timestamp TEXT UNIQUE
            )
        ''')

        cur.execute('''
            INSERT INTO users (class, no, timestamp) 
            VALUES (?, ?, ?)
        ''', (a, object_count, now))
        conn.commit()
        conn.close()

        # Optionally, return the image URL or JSON response
        return jsonify({
            "message": "Prediction successful",
            "result_image": result_path,
            "results": str(results[0].boxes)
        })

if __name__ == "__main__":
    app.run(debug=True)

