"""SuperKart sales forecasting API.

Routes
  GET  /                -> welcome message
  GET  /health          -> liveness check and expected feature list
  POST /v1/predict      -> JSON body with one product, returns {"Sales": value}
  POST /v1/predictbatch -> CSV upload in form field 'file', returns {row_index: value}
"""
import joblib
import pandas as pd
from flask import Flask, jsonify, request

superkart_api = Flask("SuperKart")
# Keep batch results in row order instead of alphabetical key order
superkart_api.json.sort_keys = False

# The serialized pipeline contains the encoder and the regressor
model = joblib.load("superkart_model.joblib")

FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]
NUMERIC_FEATURES = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]


def error(message, status=400):
    return jsonify({"error": message}), status


def prepare(frame):
    """Return (features, error_message) after checking required columns and numeric types."""
    missing = [f for f in FEATURES if f not in frame.columns]
    if missing:
        return None, f"Missing fields: {missing}"
    features = frame[FEATURES].copy()
    try:
        features[NUMERIC_FEATURES] = features[NUMERIC_FEATURES].astype(float)
    except (TypeError, ValueError):
        return None, f"These fields must be numeric: {NUMERIC_FEATURES}"
    if features.isnull().any().any():
        return None, "Input contains empty values."
    return features, None


@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecasting API"


@superkart_api.get("/health")
def health():
    return jsonify({"status": "ok", "features": FEATURES})


@superkart_api.post("/v1/predict")
def predict_sales():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error("Request body must be a JSON object with the product and store fields.")

    features, message = prepare(pd.DataFrame([payload]))
    if message:
        return error(message)

    prediction = float(model.predict(features)[0])
    return jsonify({"Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return error("Upload a CSV file in the 'file' form field.")
    try:
        input_data = pd.read_csv(request.files["file"])
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        return error("The uploaded file could not be read as CSV.")
    if input_data.empty:
        return error("The uploaded CSV has no rows.")

    features, message = prepare(input_data)
    if message:
        return error(message)

    predictions = model.predict(features)
    return jsonify({str(i): round(float(p), 2) for i, p in enumerate(predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860)
