from typing import Dict, Optional
import random


class MusicSelector:
    """
    Music selection service
    In production, integrate with music library APIs (Epidemic Sound, Artlist, etc.)
    """
    
    # Example music library (replace with actual API integration)
    MUSIC_LIBRARY = {
        "energetic": [
            {"url": "music/energetic_1.mp3", "bpm": 120},
            {"url": "music/energetic_2.mp3", "bpm": 128},
        ],
        "calm": [
            {"url": "music/calm_1.mp3", "bpm": 90},
            {"url": "music/calm_2.mp3", "bpm": 85},
        ],
        "modern": [
            {"url": "music/modern_1.mp3", "bpm": 110},
            {"url": "music/modern_2.mp3", "bpm": 115},
        ]
    }
    
    def select_music(
        self,
        style: str = "energetic",
        duration: int = 30,
        product_category: Optional[str] = None
    ) -> Dict:
        """
        Select appropriate background music
        Returns music file path/URL
        """
        # Map product category to music style
        if product_category:
            style = self._map_category_to_style(product_category)
        
        # Get music options for style
        options = self.MUSIC_LIBRARY.get(style, self.MUSIC_LIBRARY["energetic"])
        
        # Select random track
        selected = random.choice(options)
        
        return {
            "url": selected["url"],
            "bpm": selected["bpm"],
            "style": style,
            "duration": duration
        }
    
    def _map_category_to_style(self, category: str) -> str:
        """Map product category to music style"""
        mapping = {
            "electronics": "modern",
            "fashion": "energetic",
            "beauty": "calm",
            "food": "energetic",
            "fitness": "energetic",
            "home": "calm"
        }
        return mapping.get(category.lower(), "energetic")













