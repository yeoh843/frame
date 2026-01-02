import httpx
from app.core.config import settings
from typing import List, Dict, Optional
import base64
import logging

logger = logging.getLogger(__name__)


class ImageEnhancementService:
    def __init__(self):
        self.api_key = settings.NANOBANANA_API_KEY
        self.base_url = "https://api.nanobanana.ai/v1"  # Nano Banana API base URL
        
        # Check if API key is set
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NANOBANANA_API_KEY is not set. Image enhancement will use fallback (return original images).")
    
    async def enhance_image_clarity(
        self,
        image_url: str
    ) -> str:
        """
        Enhance image clarity and quality using Nano Banana AI
        Returns enhanced image URL
        """
        logger.info(f"Enhancing image clarity: {image_url}")
        
        # Skip API call if no API key
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NANOBANANA_API_KEY not set, skipping enhancement, using original image")
            return image_url
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/enhance",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": image_url,
                        "enhancement_type": "clarity",
                        "options": {
                            "quality_boost": True,
                            "sharpness": True,
                            "noise_reduction": True,
                            "color_correction": True
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                enhanced_url = result.get("enhanced_image_url") or result.get("output_url")
                logger.info(f"Successfully enhanced image clarity: {enhanced_url}")
                return enhanced_url
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Image clarity enhancement failed: {error_msg}", exc_info=True)
            # If API key is missing, raise a clear error
            if "api" in error_msg.lower() or "key" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                raise Exception(f"Nano Banana API key missing or invalid. Please set NANOBANANA_API_KEY in .env file")
            # Fallback: return original image if enhancement fails
            return image_url
    
    async def generate_multiple_angles(
        self,
        image_url: str,
        num_angles: int = 6
    ) -> List[str]:
        """
        Generate multiple angles or style variations of the product image
        Returns list of image URLs (enhanced original + generated variations)
        """
        logger.info(f"Generating {num_angles} style variations for image: {image_url}")
        
        # Skip API call if no API key
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NANOBANANA_API_KEY not set, skipping style variations, using original image")
            return [image_url]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/multi-angle",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": image_url,
                        "num_variations": num_angles,
                        "styles": ["realistic", "studio", "natural", "professional", "dramatic", "bright"],
                        "angles": ["front", "side", "back", "top", "diagonal", "closeup"],
                        "options": {
                            "maintain_quality": True,
                            "consistent_lighting": False,  # Allow different lighting for variety
                            "vary_style": True,
                            "generate_styles": True
                        }
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                result = response.json()
                variation_urls = result.get("variation_urls") or result.get("angle_urls") or result.get("variations", [])
                
                # Include original enhanced image + all variations
                all_variations = [image_url] + variation_urls[:num_angles-1]
                logger.info(f"Successfully generated {len(all_variations)} style variations")
                return all_variations
        except Exception as e:
            logger.error(f"Style variation generation failed: {str(e)}", exc_info=True)
            # Fallback: return original image
            return [image_url]
    
    async def overlay_selling_points(
        self,
        image_url: str,
        selling_points: List[str],
        overlay_style: str = "modern"
    ) -> str:
        """
        Overlay product selling points as text annotations on the image
        Returns annotated image URL
        """
        logger.info(f"Overlaying {len(selling_points)} selling points on image: {image_url}")
        
        # Skip API call if no API key
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NANOBANANA_API_KEY not set, skipping overlay, using original image")
            return image_url
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/annotate",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": image_url,
                        "annotations": [
                            {
                                "text": point,
                                "position": self._calculate_text_position(i, len(selling_points)),
                                "style": {
                                    "font_size": 32,
                                    "font_weight": "bold",
                                    "color": "#FFFFFF",
                                    "background": "rgba(0,0,0,0.7)",
                                    "padding": 10,
                                    "border_radius": 8,
                                    "animation": overlay_style
                                }
                            }
                            for i, point in enumerate(selling_points)
                        ],
                        "options": {
                            "smart_placement": True,  # AI determines best text placement
                            "avoid_important_areas": True,
                            "readability": True
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                annotated_url = result.get("annotated_image_url") or result.get("output_url")
                logger.info(f"Successfully overlaid selling points: {annotated_url}")
                return annotated_url
        except Exception as e:
            logger.error(f"Selling points overlay failed: {str(e)}", exc_info=True)
            # Fallback: return original image if overlay fails
            return image_url
    
    def _calculate_text_position(self, index: int, total: int) -> Dict[str, str]:
        """Calculate optimal text position based on index"""
        positions = [
            {"x": "10%", "y": "10%"},  # Top left
            {"x": "80%", "y": "15%"},  # Top right
            {"x": "10%", "y": "75%"},  # Bottom left
            {"x": "80%", "y": "80%"}   # Bottom right
        ]
        return positions[index % len(positions)]
    
    async def enhance_image_comprehensive(
        self,
        image_url: str,
        selling_points: Optional[List[str]] = None,
        generate_angles: bool = True
    ) -> Dict[str, any]:
        """
        Comprehensive image enhancement: clarity, multiple angles, and selling points overlay
        Returns dict with:
        - enhanced_url: clarity-enhanced image
        - angles: list of angle/variation URLs
        - annotated_url: image with selling points overlay (if provided)
        """
        logger.info(f"Starting comprehensive enhancement for image: {image_url}")
        result = {
            "enhanced_url": None,
            "angles": [],
            "annotated_url": None
        }
        
        try:
            # Step 1: Enhance clarity and quality
            result["enhanced_url"] = await self.enhance_image_clarity(image_url)
            
            # Step 2: Generate multiple style variations
            if generate_angles:
                result["angles"] = await self.generate_multiple_angles(result["enhanced_url"], num_angles=6)
                logger.info(f"Generated {len(result['angles'])} style variations")
            else:
                result["angles"] = [result["enhanced_url"]]
            
            # Step 3: Overlay selling points if provided
            if selling_points and len(selling_points) > 0:
                # Use the best enhanced image for annotation
                best_image = result["enhanced_url"] or result["angles"][0] if result["angles"] else image_url
                result["annotated_url"] = await self.overlay_selling_points(
                    best_image,
                    selling_points
                )
            
            logger.info(f"Comprehensive enhancement completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive enhancement failed: {str(e)}", exc_info=True)
            # Return fallback values
            result["enhanced_url"] = image_url
            result["angles"] = [image_url]
            if selling_points:
                result["annotated_url"] = image_url
            return result




