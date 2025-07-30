"""Unit tests for calendar utilities"""
import unittest
from datetime import datetime, timedelta

from src.telegram_ai_bot.utils.calendar_utils import (
    generate_calendar_link,
    parse_deadline,
    format_action_items_for_calendar
)

class TestCalendarUtils(unittest.TestCase):
    
    def test_generate_calendar_link(self):
        """Test calendar link generation"""
        link = generate_calendar_link(
            title="Test Event",
            description="Test Description"
        )
        
        self.assertIn("calendar.google.com", link)
        self.assertIn("Test%20Event", link)
        self.assertIn("Test%20Description", link)
        
    def test_parse_deadline_keywords(self):
        """Test deadline parsing with keywords"""
        base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Test "tomorrow"
        deadline = parse_deadline("Meeting tomorrow")
        expected = base_time + timedelta(days=1)
        self.assertEqual(deadline.date(), expected.date())
        
        # Test "today"
        deadline = parse_deadline("Submit report today")
        self.assertEqual(deadline.date(), base_time.date())
        
    def test_parse_deadline_times(self):
        """Test deadline parsing with specific times"""
        # Test PM time
        deadline = parse_deadline("Call at 3 PM")
        self.assertEqual(deadline.hour, 15)
        
        # Test AM time
        deadline = parse_deadline("Meeting at 9 AM")
        self.assertEqual(deadline.hour, 9)
        
        # Test 24-hour format
        deadline = parse_deadline("Deadline at 14:30")
        self.assertEqual(deadline.hour, 14)
        self.assertEqual(deadline.minute, 30)
        
    def test_format_action_items(self):
        """Test formatting action items with calendar links"""
        action_items = [
            {
                'task': 'Complete project',
                'deadline': 'tomorrow at 5 PM',
                'priority': 'high'
            }
        ]
        
        formatted = format_action_items_for_calendar(action_items)
        
        self.assertEqual(len(formatted), 1)
        self.assertIn('calendar_link', formatted[0])
        self.assertIn('calendar.google.com', formatted[0]['calendar_link'])

if __name__ == '__main__':
    unittest.main()