import io
import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")
TRAINED_STORE_TYPES = {"Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"}
PREFIX_LABELS = {"FD": "FD - Food", "DR": "DR - Drinks", "NC": "NC - Non-consumables"}

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Forecast the total sales of a product in a store, for one product or a whole CSV file.")


def error_message(response):
    try:
        return response.json().get("error", response.text)
    except ValueError:
        return response.text


# ----- Single prediction -----
st.header("Single product")
product_col, store_col = st.columns(2)
with product_col:
    st.subheader("Product")
    product_id_char = st.selectbox("Product family", list(PREFIX_LABELS), format_func=PREFIX_LABELS.get)
    product_type_category = st.selectbox("Product category", ["Perishables", "Non Perishables"], index=1)
    product_sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
    product_weight = st.number_input("Weight", min_value=0.0, value=12.66, step=0.1)
    product_mrp = st.number_input("MRP", min_value=0.0, value=117.08, step=1.0)
    product_allocated_area = st.number_input(
        "Allocated display area (share of store)", min_value=0.0, max_value=1.0,
        value=0.027, step=0.001, format="%.3f")
with store_col:
    st.subheader("Store")
    store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2", "Supermarket Type3",
                                              "Departmental Store", "Food Mart"], index=1)
    store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
    store_city = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

if store_type not in TRAINED_STORE_TYPES:
    st.warning(f"{store_type} was not in the training data; treat this forecast as directional.")

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_city,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age,
    "Product_Type_Category": product_type_category,
}

if st.button("Predict sales", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
    except requests.RequestException:
        st.error(f"Could not reach the prediction API at {BACKEND_URL}.")
    else:
        if response.ok:
            st.success(f"Forecast total sales: {response.json()['Sales']:,.2f}")
        else:
            st.error(error_message(response))

# ----- Batch prediction -----
st.header("Batch forecast")
st.caption("The CSV needs these columns: " + ", ".join(payload))
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None and st.button("Predict for batch", type="primary"):
    file_bytes = uploaded_file.getvalue()
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                 files={"file": (uploaded_file.name, file_bytes, "text/csv")}, timeout=120)
    except requests.RequestException:
        st.error(f"Could not reach the prediction API at {BACKEND_URL}.")
    else:
        if response.ok:
            predictions = response.json()
            results = pd.read_csv(io.BytesIO(file_bytes))
            results["Predicted_Sales"] = [predictions[str(i)] for i in range(len(results))]

            st.success(f"Forecast {len(results)} products, total {results['Predicted_Sales'].sum():,.0f}.")
            unseen = sorted(set(results["Store_Type"]) - TRAINED_STORE_TYPES)
            if unseen:
                st.warning(f"Store types not in training data: {', '.join(unseen)}. Those rows are directional.")
            st.dataframe(results, use_container_width=True)
            st.download_button("Download predictions as CSV", results.to_csv(index=False),
                               file_name="superkart_predictions.csv", mime="text/csv")
        else:
            st.error(error_message(response))
