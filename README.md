# SuperKart Sales Forecast

Forecasts the total sales of each product in each SuperKart store, so the business can plan
inventory, procurement and regional sales strategy for the upcoming quarter.

The solution has two independently deployable services:

| Folder | Service | Port |
|---|---|---|
| [`backend/`](backend/README.md) | Flask REST API serving the trained model | 7860 |
| [`frontend/`](frontend/README.md) | Streamlit app for single and batch forecasts | 8501 |

```
Browser -> Streamlit frontend (8501) -> Flask backend (7860) -> superkart_model.joblib
```

## Model summary

- Trained on 8,763 historical product-store sales records from 4 stores.
- Selected model: tuned XGBoost inside a scikit-learn pipeline (one-hot encoding + regressor),
  chosen over Random Forest, Gradient Boosting and a linear baseline.
- Test performance: R-squared 0.923, RMSE 297, MAE 123, MAPE 5.3%.
- Main drivers: the store profile, then product MRP and weight.

## Quick start (GitHub Codespaces)

```bash
docker network create superkart-net

cd backend
docker build -t superkart-backend .
docker run -d --name backend --network superkart-net -p 7860:7860 superkart-backend

cd ../frontend
docker build -t superkart-frontend .
docker run -d --name frontend --network superkart-net -p 8501:8501 superkart-frontend

docker ps
```

Then, in the **Ports** tab, set port 7860 to **Public** to call the API from outside the
Codespace, and open port 8501 to use the app.

## API at a glance

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/v1/predict` | One product (JSON) -> `{"Sales": value}` |
| POST | `/v1/predictbatch` | CSV upload -> `{row_index: value}` |

Full request and response details are in [`backend/README.md`](backend/README.md).

## Limitations

- Only four stores exist in the training data, and each has a single size, city tier and type,
  so forecasts for new store formats or new attribute combinations are directional.
- The data has no dates, so the model forecasts sales levels per product and store, not
  seasonality. Retrain each quarter as new sales data arrives.

Author: Sandeep Belkhode
