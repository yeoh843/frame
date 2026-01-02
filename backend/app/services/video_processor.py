import ffmpeg
import os
import tempfile
from typing import List, Dict, Optional
from pathlib import Path


class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def combine_clips(
        self,
        video_paths: List[str],
        output_path: str,
        transitions: List[str] = None
    ) -> str:
        """
        Combine multiple video clips with transitions
        """
        if not video_paths:
            raise ValueError("No video clips provided")
        
        # Create concat file for FFmpeg
        concat_file = os.path.join(self.temp_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # Build FFmpeg command
        stream = ffmpeg.input(concat_file, format="concat", safe=0)
        stream = ffmpeg.output(stream, output_path, vcodec="libx264", acodec="aac")
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return output_path
    
    def add_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict],
        output_path: str,
        style: str = "large_centered"
    ) -> str:
        """
        Add subtitles to video
        subtitles: [{"text": "...", "start_time": 0, "end_time": 5}, ...]
        """
        # Create SRT file
        srt_file = os.path.join(self.temp_dir, "subtitles.srt")
        with open(srt_file, "w", encoding="utf-8") as f:
            for i, subtitle in enumerate(subtitles, 1):
                start = self._format_timestamp(subtitle["start_time"])
                end = self._format_timestamp(subtitle["end_time"])
                f.write(f"{i}\n{start} --> {end}\n{subtitle['text']}\n\n")
        
        # Apply subtitle style based on style parameter
        if style == "large_centered":
            subtitle_style = (
                "FontName=Arial,FontSize=48,PrimaryColour=&Hffffff,"
                "OutlineColour=&H000000,Outline=2,Alignment=10"
            )
        else:
            subtitle_style = "FontName=Arial,FontSize=36,PrimaryColour=&Hffffff"
        
        # Add subtitles to video
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vf=f"subtitles={srt_file}:force_style='{subtitle_style}'",
            vcodec="libx264",
            acodec="copy"
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return output_path
    
    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        music_path: Optional[str] = None,
        music_volume: float = 0.3
    ) -> str:
        """
        Add voiceover and optional background music
        """
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        
        if music_path:
            music = ffmpeg.input(music_path)
            # Mix voiceover and music
            audio = ffmpeg.filter([audio, music], "amix", inputs=2, duration="longest")
            # Adjust music volume
            audio = ffmpeg.filter(audio, "volume", volume=music_volume)
        
        stream = ffmpeg.output(
            video,
            audio,
            output_path,
            vcodec="copy",
            acodec="aac",
            strict="experimental"
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return output_path
    
    def resize_video(
        self,
        video_path: str,
        output_path: str,
        aspect_ratio: str,
        width: int = None,
        height: int = None
    ) -> str:
        """
        Resize video to specific aspect ratio
        aspect_ratio: "9:16", "1:1", "16:9"
        """
        # Calculate dimensions
        if aspect_ratio == "9:16":
            target_width, target_height = 1080, 1920
        elif aspect_ratio == "1:1":
            target_width, target_height = 1080, 1080
        elif aspect_ratio == "16:9":
            target_width, target_height = 1920, 1080
        else:
            target_width, target_height = width or 1920, height or 1080
        
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vf=f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2",
            vcodec="libx264",
            acodec="copy"
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return output_path
    
    def sync_to_beat(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        """
        Sync video cuts to music beat
        """
        # Extract audio for beat detection
        audio_stream = ffmpeg.input(audio_path)
        
        # This is a simplified version - in production, use audio analysis
        # to detect beats and adjust video cuts accordingly
        video = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            video,
            audio_stream,
            output_path,
            vcodec="libx264",
            acodec="aac"
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return output_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)













