# Antigravity Notification Service

A high-throughput, GCP-native Notification Service built with FastAPI and Python 3.11+, optimized for the Antigravity framework.

## Architecture

- **FastAPI**: Non-blocking I/O for API requests.
- **Google Cloud Firestore**: Persistent state management for OTPs with atomic lifecycle.
- **Google Cloud Pub/Sub**: Message queuing to ensure internal API latency remains under 100ms.
- **Modular Adapters**: Abstracted notification provider (Twilio, SendGrid).
- **Secret Manager**: Secure credential management.

## Directory Structure

```text
├── app/
│   ├── api/          # API Route handlers
│   ├── core/         # Config, Pub/Sub, and Infrastructure
│   ├── models/       # Pydantic schemas
│   ├── notifications/# Adapter implementations (Twilio, SendGrid)
│   ├── otp/          # OTP generation and validation logic
│   └── main.py       # App entry point
├── Dockerfile        # Container configuration
├── service.yaml      # Cloud Run deployment configuration
└── requirements.txt  # Dependencies
```

## Flow Overview

1. **API Request**: User calls `POST /api/v1/notify` or `/api/v1/otp/generate`.
2. **Pub/Sub Publish**: Metadata is pushed to GCP Topic (<100ms response).
3. **Background Processing**: Google Cloud Pub/Sub triggers the **Worker Endpoint** (`POST /api/v1/worker/process`) via a Push subscription.
4. **Adapter Execution**: The worker decodes the message and uses the chosen adapter (Twilio/SendGrid) to deliver the message.
5. **OTP Management**: `/api/v1/otp/verify` consumes tokens atomically from Firestore.

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run service: `python app/main.py`
3. Access Docs: [http://localhost:8080/docs](http://localhost:8080/docs)

## Deployment

Deploy using the provided `service.yaml` via Antigravity’s CI/CD pipeline or directly to Cloud Run:
```bash
gcloud run deploy notification-service --source . --region <REGION>
```
