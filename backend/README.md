# SuperKart Sales Forecast API (backend)

Flask REST API that serves the SuperKart sales forecasting model. It predicts
`Product_Store_Sales_Total` (total sales of a product in a store) from product and store attributes.

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask application (`superkart_api`) with the prediction endpoints |
| `superkart_model.joblib` | Serialized scikit-learn pipeline: one-hot encoder + tuned XGBoost regressor |
| `requirements.txt` | Pinned Python dependencies (must match the versions used to save the model) |
| `Dockerfile` | Container image served by Gunicorn on port 7860 |

## Model

- Algorithm: XGBoost regressor tuned with 3-fold `GridSearchCV`
  (learning rate 0.1, max depth 5, 100 trees)
- Test set (30% holdout): R-squared 0.923, RMSE 297, MAE 123, MAPE 5.3%
- 5-fold cross-validated R-squared: 0.928

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Liveness check; returns `{"status": "ok", "features": [...]}` |
| POST | `/v1/predict` | Forecast for one product (JSON body) |
| POST | `/v1/predictbatch` | Forecasts for a CSV file uploaded in form field `file` |

### Input fields (JSON keys or CSV columns)

| Field | Type | Allowed values / example |
|---|---|---|
| `Product_Weight` | number | 12.66 |
| `Product_Sugar_Content` | text | Low Sugar, Regular, No Sugar |
| `Product_Allocated_Area` | number | share of display area, 0 to 1 (0.027) |
| `Product_MRP` | number | 117.08 |
| `Store_Size` | text | Small, Medium, High |
| `Store_Location_City_Type` | text | Tier 1, Tier 2, Tier 3 |
| `Store_Type` | text | Supermarket Type1, Supermarket Type2, Departmental Store, Food Mart |
| `Product_Id_char` | text | FD (food), DR (drinks), NC (non-consumables) |
| `Store_Age_Years` | number | 16 |
| `Product_Type_Category` | text | Perishables, Non Perishables |

Unseen category values (for example `Supermarket Type3`) are accepted and scored, but those
forecasts are extrapolations because the model never saw them in training.

### Single prediction

```bash
curl -X POST http://localhost:7860/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"Product_Weight": 12.66, "Product_Sugar_Content": "Low Sugar", "Product_Allocated_Area": 0.027,
       "Product_MRP": 117.08, "Store_Size": "Medium", "Store_Location_City_Type": "Tier 2",
       "Store_Type": "Supermarket Type2", "Product_Id_char": "FD", "Store_Age_Years": 16,
       "Product_Type_Category": "Non Perishables"}'
```

Response `200`: `{"Sales": 2932.6}`

### Batch prediction

```bash
curl -X POST http://localhost:7860/v1/predictbatch -F "file=@Batch_Data_SuperKart.csv"
```

Response `200`: `{"0": 1866.05, "1": 2512.14, ...}` (key = row index in the uploaded file)

### Errors

Invalid requests return HTTP `400` with `{"error": "<message>"}`:

| Cause | Example message |
|---|---|
| Body is not a JSON object | `Request body must be a JSON object ...` |
| Required field missing | `Missing fields: ['Product_MRP', ...]` |
| Non-numeric value in a numeric field | `These fields must be numeric: [...]` |
| Empty value | `Input contains empty values.` |
| No file uploaded | `Upload a CSV file in the 'file' form field.` |
| File is not valid CSV | `The uploaded file could not be read as CSV.` |
| CSV has a header but no rows | `The uploaded CSV has no rows.` |

## Run with Docker

```bash
docker network create superkart-net            # shared with the frontend container
docker build -t superkart-backend .
docker run -d --name backend --network superkart-net -p 7860:7860 superkart-backend
curl http://localhost:7860/health
```

The container name must be `backend`: the frontend reaches the API at `http://backend:7860`.
The image runs as a non-root user and has a Docker `HEALTHCHECK` on `/health`.

## Run without Docker

```bash
pip install -r requirements.txt
python app.py              # development server on port 7860
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Error loading `superkart_model.joblib` | Install the exact versions in `requirements.txt`; the model must be loaded with the library versions it was saved with |
| `docker ps` shows `(unhealthy)` | Check `docker logs backend` for a startup error |
| Codespace URL returns 401 or a login page | Set port 7860 to **Public** in the Ports tab |
| Port 7860 already in use | `docker rm -f backend`, then run the container again |

Author: Sandeep Belkhode
