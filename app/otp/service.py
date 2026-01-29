import secrets
import datetime
from typing import Optional
from google.cloud import firestore
from app.core.config import get_settings

settings = get_settings()

class OTPService:
    def __init__(self):
        self.db = firestore.Client(project=settings.PROJECT_ID)
        self.collection = self.db.collection(settings.OTP_COLLECTION)

    def generate_otp(self) -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return "".join([str(secrets.randbelow(10)) for _ in range(6)])

    async def create_otp(self, identifier: str) -> str:
        """Create and store an OTP in Firestore with a TTL."""
        otp = self.generate_otp()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.OTP_TTL_MINUTES)
        
        doc_ref = self.collection.document(identifier)
        doc_ref.set({
            "otp": otp,
            "used": False,
            "expires_at": expires_at,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return otp

    async def validate_otp(self, identifier: str, otp: str) -> bool:
        """
        Validate and atomically delete/mark the OTP as used.
        Handles race conditions using Firestore transactions or atomic deletes.
        """
        doc_ref = self.collection.document(identifier)
        
        @firestore.transactional
        def validate_in_transaction(transaction, doc_ref):
            snapshot = doc_ref.get(transaction=transaction)
            if not snapshot.exists:
                return False
            
            data = snapshot.to_dict()
            if data.get("used") or data.get("otp") != otp:
                return False
            
            # Check expiration
            expires_at = data.get("expires_at")
            if expires_at and expires_at < datetime.datetime.now(datetime.timezone.utc):
                transaction.delete(doc_ref)
                return False

            # Mark as used or delete (atomic)
            transaction.delete(doc_ref) 
            return True

        return validate_in_transaction(self.db.transaction(), doc_ref)
