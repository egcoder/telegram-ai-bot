"""Google Calendar integration utilities"""
from datetime import datetime, timedelta
from urllib.parse import quote
from typing import Optional, Dict, List

def generate_calendar_link(
    title: str,
    description: str,
    start_time: Optional[datetime] = None,
    duration_minutes: int = 30
) -> str:
    """Generate a Google Calendar event creation link"""
    
    # If no start time provided, use tomorrow at 9 AM
    if not start_time:
        start_time = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
    
    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Format dates for Google Calendar (YYYYMMDDTHHmmSS)
    date_format = "%Y%m%dT%H%M%S"
    start_str = start_time.strftime(date_format)
    end_str = end_time.strftime(date_format)
    
    # Build the Google Calendar URL
    base_url = "https://calendar.google.com/calendar/render"
    params = {
        "action": "TEMPLATE",
        "text": title,
        "details": description,
        "dates": f"{start_str}/{end_str}"
    }
    
    # Construct the URL with encoded parameters
    param_string = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    calendar_url = f"{base_url}?{param_string}"
    
    return calendar_url

def parse_deadline(text: str) -> Optional[datetime]:
    """Parse deadline mentions from text"""
    # Simple implementation - could be enhanced with NLP
    keywords = {
        "tomorrow": timedelta(days=1),
        "next week": timedelta(weeks=1),
        "next month": timedelta(days=30),
        "today": timedelta(days=0)
    }
    
    text_lower = text.lower()
    base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for keyword, delta in keywords.items():
        if keyword in text_lower:
            return base_time + delta
            
    # Try to parse specific times like "3 PM", "15:00"
    import re
    
    # Match patterns like "3 PM" or "3:00 PM"
    time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)?'
    match = re.search(time_pattern, text)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)
        
        if period and period.upper() == 'PM' and hour < 12:
            hour += 12
        elif period and period.upper() == 'AM' and hour == 12:
            hour = 0
            
        # If we found a time, check if it's for today or tomorrow
        result = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has already passed today, assume tomorrow
        if result < datetime.now():
            result += timedelta(days=1)
            
        return result
    
    return None

def format_action_items_for_calendar(action_items: List[Dict]) -> List[Dict]:
    """Format action items with calendar links"""
    formatted_items = []
    
    for item in action_items:
        task = item.get('task', '')
        deadline = item.get('deadline', '')
        priority = item.get('priority', 'medium')
        
        # Parse deadline if present
        deadline_dt = parse_deadline(deadline) if deadline else None
        
        # Generate calendar link
        calendar_link = generate_calendar_link(
            title=task,
            description=f"Priority: {priority}\nCreated via Telegram AI Bot",
            start_time=deadline_dt
        )
        
        formatted_items.append({
            'task': task,
            'deadline': deadline,
            'priority': priority,
            'calendar_link': calendar_link
        })
    
    return formatted_items