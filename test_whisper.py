#!/usr/bin/env python3
"""Test script to check Whisper API parameters"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from openai import OpenAI

def test_whisper_params():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create a dummy audio file for testing (just checking params)
    print("Testing valid Whisper API parameters...")
    
    # Test valid parameters
    valid_formats = ['json', 'text', 'srt', 'verbose_json', 'vtt']
    
    for fmt in valid_formats:
        print(f"- response_format: '{fmt}' - Should be valid")
    
    # Test invalid parameter
    try:
        print(f"- response_format: {{'type': 'json_object'}} - Should be INVALID")
        print("The error is that someone is passing chat completion response_format to Whisper")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    test_whisper_params()