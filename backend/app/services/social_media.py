import httpx
from app.core.config import settings
from typing import Dict, Optional


class SocialMediaService:
    def __init__(self):
        self.tiktok_key = settings.TIKTOK_CLIENT_KEY
        self.tiktok_secret = settings.TIKTOK_CLIENT_SECRET
        self.instagram_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.youtube_client_id = settings.YOUTUBE_CLIENT_ID
        self.youtube_client_secret = settings.YOUTUBE_CLIENT_SECRET
    
    async def publish_to_tiktok(
        self,
        video_url: str,
        caption: str,
        access_token: str
    ) -> Dict:
        """Publish video to TikTok"""
        try:
            async with httpx.AsyncClient() as client:
                # TikTok API requires video to be uploaded first
                # This is a simplified example
                response = await client.post(
                    "https://open.tiktokapis.com/v2/post/publish/",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "post_info": {
                            "title": caption,
                            "privacy_level": "PUBLIC_TO_EVERYONE",
                            "disable_duet": False,
                            "disable_comment": False,
                            "disable_stitch": False
                        },
                        "source_info": {
                            "source": "FILE_UPLOAD",
                            "video_url": video_url
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"TikTok publish failed: {str(e)}")
    
    async def publish_to_instagram(
        self,
        video_url: str,
        caption: str,
        access_token: str
    ) -> Dict:
        """Publish video to Instagram"""
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Create media container
                container_response = await client.post(
                    f"https://graph.instagram.com/v18.0/me/media",
                    params={
                        "media_type": "REELS",
                        "video_url": video_url,
                        "caption": caption,
                        "access_token": access_token
                    },
                    timeout=30.0
                )
                container_response.raise_for_status()
                container_id = container_response.json().get("id")
                
                # Step 2: Publish media
                publish_response = await client.post(
                    f"https://graph.instagram.com/v18.0/me/media_publish",
                    params={
                        "creation_id": container_id,
                        "access_token": access_token
                    },
                    timeout=30.0
                )
                publish_response.raise_for_status()
                return publish_response.json()
        except Exception as e:
            raise Exception(f"Instagram publish failed: {str(e)}")
    
    async def publish_to_youtube(
        self,
        video_url: str,
        title: str,
        description: str,
        access_token: str
    ) -> Dict:
        """Publish video to YouTube"""
        try:
            # YouTube requires OAuth2 and video file upload
            # This is a simplified example - in production, use Google API client
            async with httpx.AsyncClient() as client:
                # Note: YouTube API requires actual file upload, not just URL
                # This would need to download the video first
                raise NotImplementedError("YouTube upload requires file download and OAuth2 flow")
        except Exception as e:
            raise Exception(f"YouTube publish failed: {str(e)}")













