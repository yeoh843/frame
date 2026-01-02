import httpx
from app.core.config import settings
from typing import List, Dict, Optional
import asyncio
import base64
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class RunwayVideoService:
    def __init__(self):
        self.api_key = settings.RUNWAY_API_KEY
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.api_version = "2024-11-06"  # Updated API version
    
    async def test_api_key(self) -> bool:
        """Test if API key is valid by making a simple API call"""
        if not self.api_key or not self.api_key.strip():
            return False
        try:
            async with httpx.AsyncClient() as client:
                # Try to list models or check account status
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-Runway-Version": self.api_version
                    },
                    timeout=10.0
                )
                return response.status_code == 200
        except:
            return False
    
    async def generate_video(
        self,
        image_url: str,
        prompt: str,
        motion_bucket_id: int = 127,
        aspect_ratio: str = "16:9",
        model: str = "gen4_turbo"
    ) -> str:
        """
        Generate video from image using Runway Gen-4
        Returns video URL
        """
        # Check if API key is configured
        if not self.api_key or not self.api_key.strip() or self.api_key.strip() == "":
            raise Exception("RUNWAY_API_KEY is not configured. Please add your Runway API key to backend/.env file.")
        
        # Map aspect ratio to Runway's supported ratios
        ratio_map = {
            "16:9": "1280:720",
            "9:16": "720:1280",
            "4:3": "1104:832",
            "3:4": "832:1104",
            "1:1": "960:960",
            "21:9": "1584:672"
        }
        runway_ratio = ratio_map.get(aspect_ratio, "1280:720")  # Default to 16:9
        
        # ALWAYS compress and convert images to base64 (Runway has size limits for ALL images)
        # This ensures ALL users' images work, regardless of original size
        prompt_image = image_url
        try:
            # Make absolute URL if relative
            if image_url.startswith("/local_storage"):
                image_url = f"{settings.API_BASE_URL}{image_url}"
            
            # Download image, compress/resize, and convert to base64
            logger.info(f"Downloading and compressing image for Runway: {image_url}")
            async with httpx.AsyncClient() as download_client:
                response = await download_client.get(image_url, timeout=10.0)
                response.raise_for_status()
                image_data = response.content
                
                # ALWAYS compress and resize image to reduce size (Runway has size limits)
                # This ensures ALL users can upload any image size
                try:
                    img = Image.open(BytesIO(image_data))
                    original_size = len(image_data)
                    logger.info(f"Original image size: {original_size} bytes ({original_size / 1024 / 1024:.2f} MB), dimensions: {img.size}")
                    
                    # Resize if too large (max 1920x1080 for Runway)
                    max_width, max_height = 1920, 1080
                    if img.width > max_width or img.height > max_height:
                        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        logger.info(f"Resized image to: {img.size}")
                    
                    # Convert to JPEG with compression to reduce size (smaller than PNG)
                    output = BytesIO()
                    # Convert RGBA to RGB if needed (JPEG doesn't support transparency)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as JPEG with quality 85 (good balance between quality and size)
                    img.save(output, format='JPEG', quality=85, optimize=True)
                    compressed_data = output.getvalue()
                    compressed_size = len(compressed_data)
                    reduction = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
                    logger.info(f"Compressed image size: {compressed_size} bytes ({compressed_size / 1024 / 1024:.2f} MB) - reduced by {reduction:.1f}%")
                    
                    # Check if still too large (Runway typically has ~10MB limit for base64)
                    # Base64 increases size by ~33%, so we want raw image < 7.5MB
                    max_raw_size = 7_500_000
                    if compressed_size > max_raw_size:
                        # Further compress with lower quality
                        logger.warning(f"Image still too large ({compressed_size} bytes), applying aggressive compression")
                        output = BytesIO()
                        quality = 70
                        while compressed_size > max_raw_size and quality > 30:
                            output = BytesIO()
                            img.save(output, format='JPEG', quality=quality, optimize=True)
                            compressed_data = output.getvalue()
                            compressed_size = len(compressed_data)
                            quality -= 10
                            logger.info(f"Compressed with quality {quality}: {compressed_size} bytes ({compressed_size / 1024 / 1024:.2f} MB)")
                        
                        if compressed_size > max_raw_size:
                            raise Exception(f"Image too large even after compression: {compressed_size} bytes. Please use a smaller image.")
                    
                    image_data = compressed_data
                    mime_type = 'image/jpeg'
                except Exception as e:
                    logger.warning(f"Failed to compress image, using original: {str(e)}")
                    # Fallback to original if compression fails
                    content_type = response.headers.get('content-type', '')
                    if not content_type:
                        if image_url.lower().endswith('.png'):
                            mime_type = 'image/png'
                        elif image_url.lower().endswith('.gif'):
                            mime_type = 'image/gif'
                        else:
                            mime_type = 'image/jpeg'
                    elif 'png' in content_type.lower():
                        mime_type = 'image/png'
                    elif 'gif' in content_type.lower():
                        mime_type = 'image/gif'
                    else:
                        mime_type = 'image/jpeg'
                
                base64_image = base64.b64encode(image_data).decode('utf-8')
                base64_size = len(base64_image)
                logger.info(f"Base64 size: {base64_size} chars ({base64_size / 1024 / 1024:.2f} MB)")
                
                # Create data URI
                prompt_image = f"data:{mime_type};base64,{base64_image}"
                logger.info(f"Successfully compressed and converted image to base64 (final size: {base64_size} chars)")
        except Exception as e:
            logger.error(f"Failed to process image for Runway: {str(e)}", exc_info=True)
            raise Exception(f"Failed to load image for Runway video generation: {str(e)}")
        
        try:
            async with httpx.AsyncClient() as client:
                # Prepare request payload
                payload = {
                    "model": model,
                    "promptImage": prompt_image,
                    "promptText": prompt,
                    "motionBucket": motion_bucket_id,
                    "ratio": runway_ratio,
                    "watermark": False
                }
                
                # Log request details (without full base64 image)
                base64_preview = prompt_image[:100] + "..." if len(prompt_image) > 100 else prompt_image
                logger.info(f"Sending request to Runway API: {self.base_url}/image_to_video")
                logger.info(f"Payload: model={model}, promptText={prompt[:50]}..., motionBucket={motion_bucket_id}, ratio={runway_ratio}")
                logger.info(f"Image preview: {base64_preview}")
                
                # Create generation request
                response = await client.post(
                    f"{self.base_url}/image_to_video",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Runway-Version": self.api_version
                    },
                    json=payload,
                    timeout=60.0
                )
                
                # Log response details for debugging
                logger.info(f"Runway API response status: {response.status_code}")
                
                # Check for 400 Bad Request with detailed error
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {})
                        error_message = error_detail.get("message", str(error_data)) if isinstance(error_detail, dict) else str(error_data)
                        error_str = str(error_data) if isinstance(error_data, str) else str(error_data.get("error", error_data))
                        
                        logger.error(f"Runway API 400 Bad Request. Full response: {error_data}")
                        
                        # Check for specific error types
                        if "credits" in error_str.lower() or "insufficient" in error_str.lower():
                            raise Exception(f"Runway account has insufficient credits. Error: {error_str}. Please add credits to your Runway account at https://runwayml.com/account")
                        
                        raise Exception(f"Runway API validation error (400): {error_message}. This usually means invalid parameters. Check: model={model}, ratio={runway_ratio}, motionBucket={motion_bucket_id}. Full error: {error_data}")
                    except Exception as e:
                        if "credits" in str(e).lower() or "Runway API validation error" in str(e):
                            raise
                        logger.error(f"Failed to parse 400 error response: {str(e)}")
                        error_text = response.text[:500]  # First 500 chars
                        raise Exception(f"Runway API validation error (400 Bad Request). Response: {error_text}")
                
                # Check for 401 specifically before raise_for_status
                if response.status_code == 401:
                    error_detail = "401 Unauthorized"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", error_detail)
                    except:
                        pass
                    raise Exception(f"RUNWAY_API_KEY is invalid, expired, or revoked. Error: {error_detail}. Please check your Runway API key at https://runwayml.com/api and update backend/.env file.")
                
                response.raise_for_status()
                result = response.json()
                
                # Log the full response to understand structure
                logger.info(f"Runway API response: {result}")
                
                # Check if the response already contains the video URL (synchronous response)
                if "output" in result or "video_url" in result or "url" in result:
                    output = result.get("output") or result.get("video_url") or result.get("url")
                    if output:
                        if isinstance(output, list) and len(output) > 0:
                            logger.info(f"Video URL found in immediate response: {output[0]}")
                            return output[0]
                        elif isinstance(output, str):
                            logger.info(f"Video URL found in immediate response: {output}")
                            return output
                
                # Get generation ID - check multiple possible fields
                generation_id = result.get("id") or result.get("generation_id") or result.get("task_id")
                
                if not generation_id:
                    # If no ID, check if status is already in response
                    status = result.get("status")
                    if status == "succeeded":
                        output = result.get("output", [""])
                        if output and len(output) > 0:
                            return output[0] if isinstance(output, list) else output
                    elif status == "failed":
                        raise Exception(f"Video generation failed: {result.get('error', 'Unknown error')}")
                    else:
                        raise Exception(f"Unexpected response format from Runway API. No generation ID and status is: {status}. Full response: {result}")
                
                logger.info(f"Generation ID extracted: {generation_id}")
                
                # Poll for completion
                video_url = await self._poll_generation_status(generation_id, client)
                return video_url
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", str(e))
                except:
                    error_detail = str(e)
                raise Exception(f"RUNWAY_API_KEY is invalid, expired, or missing. Error: {error_detail}. Please verify your Runway API key in backend/.env file and ensure it's a valid key from https://runwayml.com/api")
            raise Exception(f"Runway video generation failed: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            # Don't wrap our own error messages
            if "RUNWAY_API_KEY" in error_msg:
                raise
            raise Exception(f"Runway video generation failed: {error_msg}")
    
    async def _poll_generation_status(
        self,
        generation_id: str,
        client: httpx.AsyncClient,
        max_attempts: int = 120,  # Increased to 120 attempts (10 minutes) - Runway can take longer
        poll_interval: int = 5
    ) -> str:
        """Poll for video generation completion"""
        logger.info(f"Polling for video generation status: {generation_id}")
        
        # Use the correct endpoint format from Runway API documentation
        endpoints_to_try = [
            f"{self.base_url}/tasks/{generation_id}",  # Correct endpoint per Runway support
            f"{self.base_url}/generations/{generation_id}",  # Fallback
            f"{self.base_url}/image_to_video/{generation_id}",  # Fallback
        ]
        
        working_endpoint = None
        consecutive_404_count = 0
        
        for attempt in range(max_attempts):
            # If we found a working endpoint, use it; otherwise try all
            endpoints = [working_endpoint] if working_endpoint else endpoints_to_try
            
            last_error = None
            got_response = False
            
            for endpoint in endpoints:
                try:
                    if attempt % 10 == 0 or attempt < 3:  # Log every 10th attempt or first 3
                        logger.info(f"Polling endpoint: {endpoint} (attempt {attempt+1}/{max_attempts})")
                    
                    response = await client.get(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "X-Runway-Version": self.api_version
                        },
                        timeout=10.0
                    )
                    
                    # If 404, try next endpoint (but track consecutive 404s)
                    if response.status_code == 404:
                        consecutive_404_count += 1
                        if consecutive_404_count >= len(endpoints_to_try) * 3:  # If all endpoints fail 3 times
                            raise Exception(f"All polling endpoints return 404. Generation ID: {generation_id}. This suggests the polling endpoint is incorrect or the generation was never created. Please check Runway API documentation for the correct status endpoint.")
                        continue
                    
                    # If we got a successful response, remember this endpoint
                    if not working_endpoint:
                        working_endpoint = endpoint
                        logger.info(f"Found working polling endpoint: {endpoint}")
                    
                    consecutive_404_count = 0  # Reset counter on success
                    response.raise_for_status()
                    result = response.json()
                    
                    got_response = True
                    
                    # Log full response occasionally for debugging
                    if attempt % 20 == 0 or attempt < 3:
                        logger.info(f"Poll response: {result}")
                    
                    status = result.get("status")
                    if attempt % 10 == 0 or attempt < 5:  # Log status every 10th attempt
                        logger.info(f"Generation {generation_id} status: {status} (attempt {attempt+1}/{max_attempts})")
                    
                    # Check for success (Runway uses "SUCCEEDED" in uppercase)
                    status_upper = status.upper() if status else ""
                    if status_upper in ("SUCCEEDED", "SUCCESS", "COMPLETE", "COMPLETED") or status in ("succeeded", "complete", "completed"):
                        output = result.get("output") or result.get("video_url") or result.get("url") or result.get("videoUrl")
                        if output:
                            if isinstance(output, list) and len(output) > 0:
                                video_url = output[0]
                            elif isinstance(output, str):
                                video_url = output
                            elif isinstance(output, dict):
                                video_url = output.get("url") or output.get("video_url")
                            else:
                                video_url = None
                            
                            if video_url:
                                logger.info(f"Video generation succeeded: {video_url}")
                                return video_url
                            else:
                                raise Exception(f"Video generation succeeded but no output URL found. Response: {result}")
                        else:
                            raise Exception(f"Video generation succeeded but no output field found. Response: {result}")
                    
                    # Check for failure (Runway uses "FAILED" in uppercase)
                    if status_upper in ("FAILED", "ERROR", "CANCELLED") or status in ("failed", "error", "cancelled"):
                        error_msg = result.get("error") or result.get("message") or result.get("error_message") or "Unknown error"
                        raise Exception(f"Video generation failed with status '{status}': {error_msg}")
                    
                    # If status is pending/processing/running, continue polling (Runway uses "RUNNING" in uppercase)
                    if status_upper in ("RUNNING", "PENDING", "PROCESSING", "QUEUED", "IN_PROGRESS", "IN-PROGRESS") or status in ("pending", "processing", "running", "in_progress", "in-progress", "queued", None):
                        break  # Continue to wait
                    
                    # Unknown status - log warning but continue
                    logger.warning(f"Unknown status '{status}' for generation {generation_id}. Continuing to poll...")
                    break
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        last_error = e
                        consecutive_404_count += 1
                        if consecutive_404_count >= len(endpoints_to_try) * 3:
                            raise Exception(f"All polling endpoints return 404. Generation ID: {generation_id}. Check Runway API documentation for correct status endpoint.")
                        continue  # Try next endpoint
                    else:
                        logger.warning(f"HTTP error {e.response.status_code} while polling {endpoint}: {str(e)}")
                        if e.response.status_code >= 500:
                            # Server error - might be temporary, continue polling
                            got_response = True  # We got a response, just not a good one
                            break
                        last_error = e
                        break  # Don't try other endpoints for client errors
                except httpx.HTTPError as e:
                    logger.warning(f"HTTP error while polling {endpoint}: {str(e)}")
                    last_error = e
                    # Network error - might be temporary, continue after delay
                    break
                except Exception as e:
                    # Re-raise our own exceptions (like "failed" status)
                    error_msg = str(e)
                    if "Video generation" in error_msg and ("failed" in error_msg.lower() or "succeeded" in error_msg.lower() or "404" in error_msg):
                        raise
                    logger.error(f"Error while polling {endpoint}: {error_msg}")
                    last_error = e
                    break
            
            # If we got a response (even if status is pending), wait and continue
            if got_response or attempt < max_attempts - 1:
                await asyncio.sleep(poll_interval)
            else:
                # No response from any endpoint - this is a problem
                raise Exception(f"Failed to get response from any polling endpoint for generation {generation_id}. Last error: {last_error}")
        
        raise Exception(f"Video generation timeout after {max_attempts} attempts ({max_attempts * poll_interval} seconds = {max_attempts * poll_interval / 60:.1f} minutes). Generation ID: {generation_id}. The generation may still be processing on Runway's side - check your Runway dashboard.")
    
    async def generate_batch(
        self,
        image_urls: List[str],
        prompts: List[str],
        aspect_ratio: str = "16:9"
    ) -> List[str]:
        """Generate multiple videos in parallel"""
        tasks = [
            self.generate_video(img_url, prompt, aspect_ratio=aspect_ratio)
            for img_url, prompt in zip(image_urls, prompts)
        ]
        return await asyncio.gather(*tasks)






