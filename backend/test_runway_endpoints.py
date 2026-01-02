import asyncio
import httpx
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

async def test_endpoints():
    """Test different Runway API endpoint formats"""
    api_key = settings.RUNWAY_API_KEY
    
    if not api_key:
        print("ERROR: RUNWAY_API_KEY not set")
        return
    
    base_urls = [
        "https://api.dev.runwayml.com",
        "https://api.runwayml.com"
    ]
    
    endpoints = [
        "/v1/image-to-video",
        "/v1/gen3/image-to-video",
        "/v1/generations/image-to-video",
        "/gen3/image-to-video",
        "/generations/image-to-video",
        "/image-to-video"
    ]
    
    print(f"Testing API key: {api_key[:25]}...{api_key[-10:]}\n")
    
    for base_url in base_urls:
        print(f"\n{'='*60}")
        print(f"Testing base URL: {base_url}")
        print('='*60)
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting: {url}")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "X-Runway-Version": "2024-09-13"
                        },
                        json={
                            "image_url": "https://example.com/test.jpg",
                            "prompt": "test"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                        print(f"  [SUCCESS] Status: {response.status_code}")
                        print(f"  Response: {response.text[:200]}")
                        print(f"\n[CORRECT ENDPOINT FOUND]: {url}")
                        return url
                    elif response.status_code == 401:
                        print(f"  [401] Unauthorized (key might be invalid)")
                        try:
                            error = response.json()
                            print(f"  Error: {error.get('error', 'Unknown')}")
                        except:
                            pass
                    elif response.status_code == 404:
                        print(f"  [404] Not Found")
                    elif response.status_code == 400:
                        print(f"  [400] Bad Request (endpoint exists but params wrong)")
                        try:
                            error = response.json()
                            print(f"  Error: {error.get('error', 'Unknown')}")
                            print(f"  [ENDPOINT EXISTS] Just need correct parameters")
                            return url
                        except:
                            pass
                    else:
                        print(f"  Status: {response.status_code}")
                        print(f"  Response: {response.text[:200]}")
            except Exception as e:
                print(f"  Exception: {type(e).__name__}: {str(e)[:100]}")
    
    print("\n[ERROR] No working endpoint found. Check Runway API documentation.")

if __name__ == "__main__":
    asyncio.run(test_endpoints())

