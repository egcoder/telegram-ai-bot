#!/usr/bin/env python3
"""Direct test of transcription to isolate the issue"""
import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_transcription():
    """Test the exact transcription path used by the bot"""
    from telegram_ai_bot.core.config import Config
    from telegram_ai_bot.utils.ai_service import AIService
    
    # Initialize config and service
    config = Config()
    ai_service = AIService(config.OPENAI_API_KEY, config.GPT_MODEL)
    
    print(f"OpenAI API Key present: {bool(config.OPENAI_API_KEY)}")
    print(f"Using model: {config.GPT_MODEL}")
    
    # Create a test audio file
    import wave
    import struct
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        with wave.open(tmp.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            
            # Write 2 seconds of silence
            for _ in range(32000):
                wav_file.writeframes(struct.pack('<h', 0))
        
        audio_path = Path(tmp.name)
    
    print(f"\nTest audio file created: {audio_path}")
    print(f"File size: {audio_path.stat().st_size} bytes")
    
    # Test transcription
    try:
        print("\nCalling ai_service.transcribe_audio()...")
        transcript = await ai_service.transcribe_audio(audio_path)
        print(f"SUCCESS! Transcript: {transcript}")
    except Exception as e:
        print(f"FAILED with error: {e}")
        print(f"Error type: {type(e)}")
        
        # Check if it's the response_format error
        if "response_format" in str(e) and "json_object" in str(e):
            print("\nERROR CONFIRMED: The json_object response_format is still being passed!")
            print("This means either:")
            print("1. The bot is not using our updated code")
            print("2. The error is coming from a different source")
            print("3. There's another OpenAI client being used somewhere")
    finally:
        # Clean up
        os.unlink(audio_path)
        
    # Also test the WhisperService directly
    print("\n\nTesting WhisperService directly...")
    try:
        from telegram_ai_bot.utils.whisper_service import WhisperService
        
        # Create another test file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            with wave.open(tmp.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                for _ in range(16000):
                    wav_file.writeframes(struct.pack('<h', 0))
            audio_path2 = Path(tmp.name)
        
        whisper = WhisperService(config.OPENAI_API_KEY)
        transcript = whisper.transcribe(audio_path2)
        print(f"WhisperService SUCCESS! Transcript: {transcript}")
        os.unlink(audio_path2)
    except Exception as e:
        print(f"WhisperService FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_transcription())