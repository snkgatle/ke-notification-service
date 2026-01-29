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

## CI/CD Pipeline

The service uses GitHub Actions for automated deployment. When you push to the `main` branch, the workflow will build a Docker image, push it to Artifact Registry, and deploy it to Cloud Run.

### GitHub Secrets Setup

To enable deployment, add the following secrets to your GitHub repository:

1. `WIF_PROVIDER`: The full identifier of your Workload Identity Provider (e.g., `projects/12345/locations/global/workloadIdentityPools/my-pool/providers/my-provider`).
2. `WIF_SERVICE_ACCOUNT`: The service account email used for deployment (e.g., `github-actions@kgatle-empire-services.iam.gserviceaccount.com`).

### Initial GCP Setup for CI/CD

Run these commands once to prepare your project:

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create notification-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Notification Service"
```

## Post-Deployment Setup (Secrets)

To use Twilio and SendGrid, you must add the following secrets to Google Secret Manager:

1. `TWILIO_ACCOUNT_SID`
2. `TWILIO_AUTH_TOKEN`
3. `TWILIO_PHONE_NUMBER`
4. `SENDGRID_API_KEY`

You can add them via the GCP Console or CLI:
```bash
echo -n "YOUR_VALUE" | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-
```

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run service: `python app/main.py`
3. Access Docs: [http://localhost:8080/docs](http://localhost:8080/docs)

## Deployment

Deploy using the provided `service.yaml` via Antigravity’s CI/CD pipeline or directly to Cloud Run:
```bash
gcloud run deploy notification-service --source . --region <REGION>
```
