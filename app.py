from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
import numpy as np
import pickle
from middleware.auth import login_required
from routes.auth_routes import auth_bp
import config

# Load Model and Scalers
try:
    model = pickle.load(open('model.pkl', 'rb'))
    sc = pickle.load(open('standscaler.pkl', 'rb'))
    mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
except FileNotFoundError as e:
    print(f"Error loading model or scalers: {e}")
    exit(1)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configure CORS
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://your-frontend-domain.com"], 
                             "supports_credentials": True}})

# Register Auth Routes
app.register_blueprint(auth_bp, url_prefix="/auth")

# Crop Dictionary
crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut",
    6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon",
    11: "Grapes", 12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil",
    16: "Blackgram", 17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas",
    20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

# 🏠 Home Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Farmer Backend API! 🌱",
        "routes": {
            "Home": "/",
            "Login": "/auth/login",
            "Register": "/auth/register",
            "Refresh": "/auth/refresh",
            "Logout": "/auth/logout",
            "Predict": "/predict"
        }
    })

# 🌾 Predict Route
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid request. No data provided"}), 400

        # Extracting features
        required_fields = ["Nitrogen", "Phosporus", "Potassium", "Temperature", "Humidity", "pH", "Rainfall"]
        feature_list = [float(data.get(field, 0)) for field in required_fields]

        # Scaling features
        single_pred = np.array(feature_list).reshape(1, -1)
        mx_features = mx.transform(single_pred)
        sc_mx_features = sc.transform(mx_features)
        prediction = model.predict(sc_mx_features)

        # Getting the crop name
        crop = crop_dict.get(prediction[0], "Unknown")
        result = f"{crop} is the best crop to be cultivated right there."
        return jsonify({"result": result})

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "An error occurred during prediction"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000,host="0.0.0.0")
