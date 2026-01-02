from openai import OpenAI
from app.core.config import settings
from typing import List, Dict
import json
import logging
import base64
import httpx

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class StoryboardService:
    def __init__(self):
        self.client = client
    
    async def generate_storyboard(
        self,
        image_urls: List[str],
        product_info: Dict = None
    ) -> Dict:
        """
        Generate storyboard with shot breakdown, subtitles, hook, selling points, and CTA.
        Returns structured JSON with:
        - Shot number
        - Image or B-roll reference (index into image_urls)
        - Text/subtitle
        - Suggested duration
        - Hook, product selling points, CTA
        """
        logger.info(f"Generating storyboard for {len(image_urls)} images")
        
        # Create image reference map for the prompt
        image_refs = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(image_urls)])
        
        prompt = f"""
You are a professional video scriptwriter for product marketing videos.
Analyze the product images and create a compelling video storyboard optimized for social media (TikTok, Instagram Reels, YouTube Shorts).

Product Images ({len(image_urls)} total):
{image_refs}

{f"Product Info: {json.dumps(product_info)}" if product_info else ""}

Create a storyboard with 3-6 shots. For each shot, you MUST provide:
1. shot_number: Sequential number starting from 1
2. image_reference: Index number (0-based) of which image from the input list to use, or "b-roll" if suggesting B-roll footage
3. text: Subtitle text (large, centered, trending style - max 5 words per subtitle)
4. duration: Suggested duration in seconds (3-8 seconds per shot is typical)
5. hook: Boolean indicating if this is the hook (first 3 seconds - attention-grabbing)
6. selling_points: Array of key product features/benefits to highlight (extracted from shot)
7. cta: Call-to-action text for the end (only the last shot should have this, others should be empty string)

IMPORTANT: 
- The first shot MUST have hook: true
- Only the LAST shot should have a non-empty cta field
- Each shot must reference an image by index (0 to {len(image_urls)-1}) or use "b-roll"
- Distribute images across shots to showcase different angles/features

Return ONLY valid JSON in this exact format:
{{
    "shots": [
        {{
            "shot_number": 1,
            "image_reference": 0,
            "text": "Introducing the Future",
            "duration": 3,
            "hook": true,
            "selling_points": ["Premium quality", "Innovative design"],
            "cta": ""
        }},
        {{
            "shot_number": 2,
            "image_reference": 1,
            "text": "Built to Last",
            "duration": 4,
            "hook": false,
            "selling_points": ["Durable materials", "Long warranty"],
            "cta": ""
        }},
        {{
            "shot_number": 3,
            "image_reference": 2,
            "text": "Shop Now",
            "duration": 3,
            "hook": false,
            "selling_points": ["Limited time offer"],
            "cta": "Shop Now - Link in Bio"
        }}
    ],
    "hook_text": "Attention-grabbing opening text",
    "main_selling_points": ["Key benefit 1", "Key benefit 2", "Key benefit 3"],
    "final_cta": "Shop Now - Link in Bio",
    "total_duration": 10
}}
"""
        
        try:
            # Use GPT-4 Vision if we have image URLs
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert video scriptwriter specializing in product marketing videos for social media platforms. You create engaging, conversion-focused content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # If we have image URLs, add them to the message using GPT-4 Vision
            if image_urls:
                content_with_images = [{"type": "text", "text": prompt}]
                # Limit to 4 images for API (GPT-4 Vision supports up to 10, but we'll be conservative)
                async with httpx.AsyncClient() as http_client:
                    for img_url in image_urls[:4]:
                        # Always convert to base64 for localhost URLs (OpenAI can't access localhost)
                        if "localhost" in img_url or "127.0.0.1" in img_url or img_url.startswith("/local_storage"):
                            try:
                                # If it's a relative path, make it absolute
                                if img_url.startswith("/local_storage"):
                                    from app.core.config import settings
                                    img_url = f"{settings.API_BASE_URL}{img_url}"
                                
                                # Download image and convert to base64
                                logger.info(f"Converting local image to base64: {img_url}")
                                response = await http_client.get(img_url, timeout=10.0)
                                response.raise_for_status()
                                image_data = response.content
                                base64_image = base64.b64encode(image_data).decode('utf-8')
                                
                                # Determine image format from URL or content type
                                content_type = response.headers.get('content-type', '')
                                if not content_type:
                                    # Guess from URL
                                    if img_url.lower().endswith('.png'):
                                        mime_type = 'image/png'
                                    elif img_url.lower().endswith('.gif'):
                                        mime_type = 'image/gif'
                                    else:
                                        mime_type = 'image/jpeg'
                                elif 'png' in content_type.lower():
                                    mime_type = 'image/png'
                                elif 'gif' in content_type.lower():
                                    mime_type = 'image/gif'
                                else:
                                    mime_type = 'image/jpeg'
                                
                                # Use base64 format for localhost images
                                content_with_images.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                })
                                logger.info(f"Successfully converted image to base64 (size: {len(base64_image)} chars)")
                            except Exception as e:
                                logger.error(f"Failed to convert local image to base64: {str(e)}", exc_info=True)
                                raise Exception(f"Failed to load image for storyboard generation: {str(e)}")
                        else:
                            # Use URL directly for public URLs
                            content_with_images.append({
                                "type": "image_url",
                                "image_url": {"url": img_url}
                            })
                messages[1]["content"] = content_with_images
            
            logger.info("Calling OpenAI API for storyboard generation")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            storyboard_json = response.choices[0].message.content
            logger.info(f"Received storyboard response from OpenAI: {len(storyboard_json)} characters")
            
            storyboard = json.loads(storyboard_json)
            
            # Validate storyboard structure
            if "shots" not in storyboard or not isinstance(storyboard["shots"], list):
                raise ValueError("Invalid storyboard format: missing 'shots' array")
            
            if len(storyboard["shots"]) < 3 or len(storyboard["shots"]) > 6:
                logger.warning(f"Storyboard has {len(storyboard['shots'])} shots, expected 3-6")
            
            # Validate each shot has required fields
            for i, shot in enumerate(storyboard["shots"]):
                required_fields = ["shot_number", "image_reference", "text", "duration"]
                for field in required_fields:
                    if field not in shot:
                        raise ValueError(f"Invalid storyboard format: shot {i+1} missing '{field}'")
            
            logger.info(f"Successfully generated storyboard with {len(storyboard['shots'])} shots")
            return storyboard
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from OpenAI response: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Response content: {response.choices[0].message.content[:500] if 'response' in locals() else 'No response'}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to generate storyboard: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    def generate_subtitles(self, storyboard: Dict) -> List[Dict]:
        """Extract and format subtitles from storyboard"""
        subtitles = []
        current_time = 0
        
        for shot in storyboard.get("shots", []):
            subtitle = {
                "text": shot.get("text", ""),  # Updated to use "text" field
                "start_time": current_time,
                "end_time": current_time + shot.get("duration", 5),
                "style": "large_centered"
            }
            subtitles.append(subtitle)
            current_time += shot.get("duration", 5)
        
        return subtitles




