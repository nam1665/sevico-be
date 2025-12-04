import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson.objectid import ObjectId
from app.config.database import get_db
from app.utils.password_helper import hash_password, verify_password
from app.utils.jwt_helper import create_access_token
from app.config.settings import get_settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.users_collection = get_db()["users"]
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    def generate_reset_token(self) -> str:
        """Generate a secure password reset token."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def register_user(self, email: str, password: str, fullname: Optional[str] = None, 
                     avatar: Optional[str] = None, dob: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password (plain text)
            fullname: User's full name (optional)
            avatar: User's avatar URL (optional)
            dob: User's date of birth (optional)
            
        Returns:
            Dictionary with user info or error
        """
        # Check if user already exists
        existing_user = self.users_collection.find_one({"email": email})
        if existing_user:
            return {"success": False, "message": "User already exists"}
        
        # Generate verification code
        verification_code = self.generate_verification_code()
        code_expires_at = datetime.utcnow() + timedelta(
            minutes=self.settings.verification_code_expiration_minutes
        )
        
        # Create user document
        user_doc = {
            "email": email,
            "password_hash": hash_password(password),
            "fullname": fullname,
            "avatar": avatar,
            "dob": dob,
            "is_verified": False,
            "verification_code": verification_code,
            "verification_code_expires_at": code_expires_at,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.users_collection.insert_one(user_doc)
        
        return {
            "success": True,
            "user_id": str(result.inserted_id),
            "email": email,
            "verification_code": verification_code  # In production, don't return this
        }
    
    def verify_email(self, email: str, verification_code: str) -> Dict[str, Any]:
        """
        Verify user email.
        
        Args:
            email: User email
            verification_code: Verification code from email
            
        Returns:
            Dictionary with success status
        """
        user = self.users_collection.find_one({"email": email})
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        if user.get("is_verified"):
            return {"success": False, "message": "User already verified"}
        
        # Check verification code
        if user.get("verification_code") != verification_code:
            return {"success": False, "message": "Invalid verification code"}
        
        # Check expiration
        expires_at = user.get("verification_code_expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            return {"success": False, "message": "Verification code expired"}
        
        # Update user
        self.users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "is_verified": True,
                    "verification_code": None,
                    "verification_code_expires_at": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"success": True, "message": "Email verified successfully"}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate JWT token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dictionary with token or error
        """
        user = self.users_collection.find_one({"email": email})
        
        if not user:
            return {"success": False, "message": "Invalid credentials"}
        
        if not user.get("is_verified"):
            return {"success": False, "message": "Email not verified"}
        
        if not verify_password(password, user.get("password_hash")):
            return {"success": False, "message": "Invalid credentials"}
        
        # Generate JWT token
        access_token = create_access_token({"sub": email})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.settings.jwt_expiration_hours * 3600,
            "email": email
        }
    
    def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Initiate password reset process.
        
        Args:
            email: User email
            
        Returns:
            Dictionary with reset token
        """
        user = self.users_collection.find_one({"email": email})
        
        if not user:
            # Return success even if user doesn't exist for security
            return {"success": True, "message": "Password reset email sent if user exists"}
        
        reset_token = self.generate_reset_token()
        token_expires_at = datetime.utcnow() + timedelta(
            hours=self.settings.password_reset_expiration_hours
        )
        
        self.users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "password_reset_token": reset_token,
                    "password_reset_token_expires_at": token_expires_at,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "reset_token": reset_token,  # In production, send via email only
            "message": "Password reset email sent"
        }
    
    def confirm_password_reset(self, email: str, reset_token: str, new_password: str) -> Dict[str, Any]:
        """
        Confirm password reset and update password.
        
        Args:
            email: User email
            reset_token: Reset token from email
            new_password: New password
            
        Returns:
            Dictionary with success status
        """
        user = self.users_collection.find_one({"email": email})
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Verify reset token
        if user.get("password_reset_token") != reset_token:
            return {"success": False, "message": "Invalid reset token"}
        
        # Check expiration
        expires_at = user.get("password_reset_token_expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            return {"success": False, "message": "Reset token expired"}
        
        # Update password
        self.users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "password_hash": hash_password(new_password),
                    "password_reset_token": None,
                    "password_reset_token_expires_at": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"success": True, "message": "Password reset successfully"}
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return self.users_collection.find_one({"email": email})


# Singleton instance
auth_service = AuthService()
