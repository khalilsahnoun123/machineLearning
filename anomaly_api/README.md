# Anomaly Detection API

This Flask API serves `anomaly_model.joblib` on port `5004`.

## Run

```powershell
pip install -r requirements.txt
python app.py
```

## Endpoints

- `GET /health`
- `POST /predict`

The Angular app calls `POST http://127.0.0.1:5004/predict` from the Anomaly Model page.
