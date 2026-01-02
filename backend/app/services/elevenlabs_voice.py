import httpx
from app.core.config import settings
from typing import Optional
import base64


class ElevenLabsVoiceService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def generate_voiceover(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice (Rachel)
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> bytes:
        """
        Generate voiceover audio from text
        Returns audio bytes (MP3)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers={
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": self.api_key
                    },
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": stability,
                            "similarity_boost": similarity_boost
                        }
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            raise Exception(f"ElevenLabs voiceover generation failed: {str(e)}")
    
    async def get_voices(self) -> list:
        """Get available voices"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json().get("voices", [])
        except Exception as e:
            print(f"Failed to get voices: {str(e)}")
            return []













