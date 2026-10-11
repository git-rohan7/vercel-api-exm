# eShopCo latency metrics API

## Deploy to Vercel
1. Push the contents of this folder to a GitHub repository.
2. In Vercel, choose **Add New → Project** and import that repository.
3. Deploy with the default Python settings.
4. The POST endpoint will be `https://YOUR-VERCEL-PROJECT.vercel.app/api/latency`.

## Request
```json
{"regions":["emea","amer"],"threshold_ms":164}
```

## Local test
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```
POST to `http://127.0.0.1:8000/api/latency`.

CORS permits any origin and POST/OPTIONS requests. Metrics are calculated from
the included telemetry.json; p95 uses linear interpolation.
