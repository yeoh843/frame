import httpx
from app.core.config import settings
from typing import List
import asyncio
import base64
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class Veo3VideoService:
    def __init__(self):
        self.api_key = settings.VEO3_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"  # Google AI Studio API
    
    async def generate_video(
        self,
        image_url: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> str:
        """
        Generate video from image using Google Veo3
        Returns video URL
        """
        if not self.api_key or not self.api_key.strip():
            raise Exception("Veo3 API key is not configured. Please contact support.")
        
        # Download and convert image to base64
        prompt_image = await self._prepare_image(image_url)
        
        try:
            async with httpx.AsyncClient() as client:
                # Google Veo3 API endpoint - update with actual endpoint
                response = await client.post(
                    f"{self.base_url}/models/veo3:predict",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image": prompt_image,
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        **kwargs
                    },
                    timeout=60.0
                )
                
                if response.status_code == 401:
                    raise Exception("Veo3 API authentication failed. Please contact support.")
                
                response.raise_for_status()
                result = response.json()
                
                # Check if video URL is in response
                video_url = result.get("video_url") or result.get("url") or result.get("output")
                if video_url:
                    if isinstance(video_url, list) and len(video_url) > 0:
                        return video_url[0]
                    return video_url
                
                # Poll for completion if async
                generation_id = result.get("id") or result.get("task_id") or result.get("generation_id")
                if generation_id:
                    return await self._poll_generation_status(generation_id, client)
                
                raise Exception(f"Unexpected response format: {result}")
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Veo3 API authentication failed. Please contact support.")
            raise Exception(f"Veo3 video generation failed: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            if "Veo3 API" in error_msg:
                raise
            raise Exception(f"Veo3 video generation failed: {error_msg}")
    
    async def _prepare_image(self, image_url: str) -> str:
        """Download, compress, and convert image to base64"""
        try:
            if image_url.startswith("/local_storage"):
                from app.core.config import settings
                image_url = f"{settings.API_BASE_URL}{image_url}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=10.0)
                response.raise_for_status()
                image_data = response.content
                
                # Compress image
                img = Image.open(BytesIO(image_data))
                max_width, max_height = 1920, 1080
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                image_data = output.getvalue()
                
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_image}"
        except Exception as e:
            logger.error(f"Failed to prepare image: {str(e)}")
            raise Exception(f"Failed to load image: {str(e)}")
    
    async def _poll_generation_status(
        self,
        generation_id: str,
        client: httpx.AsyncClient,
        max_attempts: int = 120,
        poll_interval: int = 5
    ) -> str:
        """Poll for video generation completion"""
        for attempt in range(max_attempts):
            try:
                response = await client.get(
                    f"{self.base_url}/models/veo3:getOperation?name={generation_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status", "").upper()
                if status in ("SUCCEEDED", "COMPLETE", "COMPLETED", "DONE"):
                    video_url = result.get("video_url") or result.get("url") or result.get("output")
                    if video_url:
                        if isinstance(video_url, list) and len(video_url) > 0:
                            return video_url[0]
                        return video_url
                    raise Exception(f"Video generation succeeded but no URL found: {result}")
                
                if status in ("FAILED", "ERROR"):
                    raise Exception(f"Video generation failed: {result.get('error', 'Unknown error')}")
                
                await asyncio.sleep(poll_interval)
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    await asyncio.sleep(poll_interval)
                    continue
                raise
        
        raise Exception(f"Video generation timeout after {max_attempts * poll_interval} seconds")

