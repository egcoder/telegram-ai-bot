#!/usr/bin/env python3
"""Debug script to find the exact source of response_format error"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_raw_api_call():
    """Test the most basic API call possible"""
    import requests
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    # Create minimal audio file
    import wave
    import struct
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        with wave.open(tmp.name, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            for _ in range(16000):
                wav.writeframes(struct.pack('<h', 0))
        audio_file = tmp.name
    
    print("Testing direct API call with requests...")
    
    # Test 1: Basic call
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    with open(audio_file, 'rb') as f:
        files = {
            'file': ('audio.wav', f, 'audio/wav'),
            'model': (None, 'whisper-1'),
            'response_format': (None, 'text')
        }
        
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers=headers,
            files=files
        )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    else:
        print(f"Success: {response.text}")
    
    # Test 2: Check what happens with json_object
    print("\n\nTesting with json_object (should fail)...")
    with open(audio_file, 'rb') as f:
        files = {
            'file': ('audio.wav', f, 'audio/wav'),
            'model': (None, 'whisper-1'),
            'response_format': (None, json.dumps({"type": "json_object"}))
        }
        
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers=headers,
            files=files
        )
    
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    
    os.unlink(audio_file)

def check_environment():
    """Check for any environment variables that might affect OpenAI"""
    print("\nChecking environment variables...")
    
    for key, value in os.environ.items():
        if 'OPENAI' in key.upper() and 'KEY' not in key.upper():
            print(f"{key}: {value}")
    
    # Check Python path
    print("\nPython path:")
    for path in sys.path[:5]:
        print(f"  {path}")

def test_imports():
    """Test if imports are causing issues"""
    print("\nTesting imports...")
    
    try:
        import openai
        print(f"OpenAI version: {openai.__version__}")
        print(f"OpenAI file: {openai.__file__}")
        
        # Check if there are any monkey patches
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print(f"Client type: {type(client)}")
        print(f"Client module: {client.__module__}")
        
    except Exception as e:
        print(f"Import error: {e}")

if __name__ == "__main__":
    print("=== OpenAI Whisper Debug ===\n")
    
    check_environment()
    test_imports()
    test_raw_api_call()