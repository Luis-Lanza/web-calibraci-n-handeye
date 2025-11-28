import random
import string
from datetime import datetime, timedelta

class EmailService:
    @staticmethod
    def generate_code(length=6) -> str:
        """Generate a random numeric code."""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_mfa_code(email: str, code: str):
        """
        Send MFA code to user's email.
        For development, this prints to the console.
        """
        print("\n" + "="*50)
        print(f"📧 EMAIL SIMULATION - To: {email}")
        print(f"🔐 Your MFA Verification Code is: {code}")
        print("="*50 + "\n")
        return True
