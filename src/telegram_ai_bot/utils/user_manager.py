"""User management utilities"""
import json
import logging
from pathlib import Path
from typing import Set, List, Dict, Optional

logger = logging.getLogger(__name__)

class UserManager:
    """Manages authorized users for the bot"""
    
    def __init__(self, users_file: Path, admin_user_id: Optional[str] = None):
        self.users_file = users_file
        self.admin_user_id = int(admin_user_id) if admin_user_id else None
        self._ensure_file_exists()
        self.users = self._load_users()
        
        # Always include admin in authorized users
        if self.admin_user_id and self.admin_user_id not in self.users:
            self.add_user(self.admin_user_id)
        
    def _ensure_file_exists(self):
        """Ensure the users file exists"""
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f, indent=2)
            logger.info(f"Created new users file: {self.users_file}")
            
    def _load_users(self) -> Set[int]:
        """Load authorized users from file"""
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return set(data.get('users', []))
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return set()
            
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump({"users": list(self.users)}, f, indent=2)
            logger.info(f"Saved {len(self.users)} users")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            
    def is_authorized(self, user_id: int) -> bool:
        """Check if a user is authorized"""
        return user_id in self.users
    
    def is_user_allowed(self, user_id: int) -> bool:
        """Alias for is_authorized for backward compatibility"""
        return self.is_authorized(user_id)
        
    def add_user(self, user_id: int) -> bool:
        """Add a user to the authorized list"""
        if user_id not in self.users:
            self.users.add(user_id)
            self._save_users()
            logger.info(f"Added user {user_id}")
            return True
        return False
        
    def remove_user(self, user_id: int) -> bool:
        """Remove a user from the authorized list"""
        if user_id in self.users:
            self.users.remove(user_id)
            self._save_users()
            logger.info(f"Removed user {user_id}")
            return True
        return False
        
    def get_user_count(self) -> int:
        """Get the total number of authorized users"""
        return len(self.users)
        
    def get_all_users(self) -> List[int]:
        """Get all authorized user IDs"""
        return list(self.users)
        
    def generate_invite_token(self, inviter_id: int) -> str:
        """Generate an invitation token"""
        import secrets
        import time
        
        token = secrets.token_urlsafe(16)
        # In a production environment, you'd store this in a database
        # For now, we'll use a simple in-memory approach
        return token