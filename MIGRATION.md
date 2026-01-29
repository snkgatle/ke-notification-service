# Email Provider Migration: SendGrid to Brevo

This document outlines the migration from SendGrid to Brevo (formerly Sendinblue) as the primary email provider for the Notification Service.

## Reasons for Migration
- **Cost-Efficiency**: Brevo offers a more competitive pricing model for transactional emails.
- **Regional Compliance**: Enhanced data residency options.

## Changes Made

### 1. Dependencies
- Removed `sendgrid`
- Added `sib-api-v3-sdk`

### 2. Configuration & Secrets
We have renamed the following secrets in `config.py` and Google Secret Manager:
- `SENDGRID_API_KEY` → `BREVO_API_KEY`
- `SENDGRID_FROM_EMAIL` → `BREVO_FROM_EMAIL`

### 3. Code Refactor
- `app/notifications/email.py`: The `SendGridEmailAdapter` has been replaced by `BrevoEmailAdapter`. 
- The `BaseNotifier` interface remains unchanged, ensuring the `send` method signature is consistent.
- `app/api/v1/endpoints.py`: Updated the internal worker process to instantiate the new `BrevoEmailAdapter`.

## Action Items for DevOps
- [ ] Add the `BREVO_API_KEY` secret to Google Secret Manager in the `kgatle-empire-services` project.
- [ ] Ensure `BREVO_FROM_EMAIL` is configured in the environment or Secret Manager.
- [ ] Optionally remove the legacy `SENDGRID_*` secrets after verifying the migration.

## Verification
- Run `pytest` to ensure the mock tests for Brevo integration pass.
- Verify that emails are being sent correctly in the development environment with the updated API key.
