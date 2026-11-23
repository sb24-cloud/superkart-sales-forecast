# SuperKart Sales Forecast UI (frontend)

Streamlit web app for SuperKart planners. It sends product and store details to the backend
API and shows the forecast total sales, for one product or a whole CSV file.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit application |
| `requirements.txt` | Pinned Python dependencies |
| `Dockerfile` | Container image serving the app on port 8501 |

## Features

- **Single product:** select boxes and number inputs restricted to valid values, with the
  forecast shown on one click.
- **Batch forecast:** upload a CSV, see every row with its forecast and the batch total, and
  download the results as `superkart_predictions.csv`.
- **Warnings:** a store type that was not in the training data (for example
  `Supermarket Type3`) is flagged as a directional forecast.
- **Readable errors:** API validation messages and connection failures are shown in the page
  instead of crashing the app.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `BACKEND_URL` | `http://backend:7860` | Base URL of the backend API |

The default works when both containers share a Docker network and the backend container is
named `backend`.

## Batch CSV format

The file needs these columns (extra columns are ignored by the API):
`Product_Weight`, `Product_Sugar_Content`, `Product_Allocated_Area`, `Product_MRP`,
`Store_Size`, `Store_Location_City_Type`, `Store_Type`, `Product_Id_char`,
`Store_Age_Years`, `Product_Type_Category`.
See `backend/README.md` for allowed values.

## Run with Docker

Start the backend container first (see `backend/README.md`), then:

```bash
docker build -t superkart-frontend .
docker run -d --name frontend --network superkart-net -p 8501:8501 superkart-frontend
```

Open `http://localhost:8501`, or the forwarded URL for port 8501 in a GitHub Codespace.

## Run without Docker

```bash
pip install -r requirements.txt
BACKEND_URL=http://localhost:7860 streamlit run app.py
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Could not reach the prediction API" | Check the backend is running (`docker ps`) and both containers are on `superkart-net` |
| Error about missing fields after a batch upload | The CSV is missing one of the required columns listed above |
| Page does not load in a Codespace | Open port 8501 from the Ports tab |

Author: Sandeep Belkhode
