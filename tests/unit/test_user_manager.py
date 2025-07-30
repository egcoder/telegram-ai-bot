"""Unit tests for UserManager"""
import unittest
import tempfile
import json
from pathlib import Path

from src.telegram_ai_bot.utils.user_manager import UserManager

class TestUserManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.write('{"users": []}')
        self.temp_file.close()
        self.user_manager = UserManager(Path(self.temp_file.name))
        
    def tearDown(self):
        """Clean up test environment"""
        Path(self.temp_file.name).unlink()
        
    def test_add_user(self):
        """Test adding a user"""
        user_id = 12345
        self.assertTrue(self.user_manager.add_user(user_id))
        self.assertTrue(self.user_manager.is_authorized(user_id))
        
        # Test adding same user again
        self.assertFalse(self.user_manager.add_user(user_id))
        
    def test_remove_user(self):
        """Test removing a user"""
        user_id = 12345
        self.user_manager.add_user(user_id)
        
        self.assertTrue(self.user_manager.remove_user(user_id))
        self.assertFalse(self.user_manager.is_authorized(user_id))
        
        # Test removing non-existent user
        self.assertFalse(self.user_manager.remove_user(user_id))
        
    def test_user_count(self):
        """Test user count"""
        self.assertEqual(self.user_manager.get_user_count(), 0)
        
        for i in range(5):
            self.user_manager.add_user(i)
            
        self.assertEqual(self.user_manager.get_user_count(), 5)
        
    def test_persistence(self):
        """Test that users are persisted to file"""
        user_id = 12345
        self.user_manager.add_user(user_id)
        
        # Create new manager with same file
        new_manager = UserManager(Path(self.temp_file.name))
        self.assertTrue(new_manager.is_authorized(user_id))

if __name__ == '__main__':
    unittest.main()