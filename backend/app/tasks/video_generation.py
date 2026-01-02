from celery import Celery
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Job, JobStatus
from app.services.ai_storyboard import StoryboardService
from app.services.image_enhancement import ImageEnhancementService
from app.services.seedream_video import SeedreamVideoService
from app.services.openai_video import OpenAIVideoService
from app.services.kling_video import KlingVideoService
from app.services.veo3_video import Veo3VideoService
from app.services.elevenlabs_voice import ElevenLabsVoiceService
from app.services.video_processor import VideoProcessor
from app.services.music_selector import MusicSelector
from app.services.storage import StorageService
import tempfile
import os
import asyncio
import httpx
import logging
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "video_generation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True


async def _process_video_job_async(job_id: str):
    """Async video generation workflow"""
    db = SessionLocal()
    processor = VideoProcessor()
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == UUID(job_id)).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        job.status = JobStatus.PROCESSING
        job.progress = 10
        db.commit()
        
        # Step 1: Enhance images with Nanobanana
        logger.info(f"Starting image enhancement for job {job_id}")
        enhancement_service = ImageEnhancementService()
        enhanced_images = []
        enhanced_data = []  # Store full enhancement data
        
        for idx, img_url in enumerate(job.image_urls):
            try:
                logger.info(f"Enhancing image {idx+1}/{len(job.image_urls)}: {img_url}")
                
                # Get selling points from job metadata if available, or use defaults
                selling_points = None
                if job.options and "selling_points" in job.options:
                    selling_points = job.options.get("selling_points")
                
                # Comprehensive enhancement: clarity, multiple style variations, and annotations
                enhancement_result = await enhancement_service.enhance_image_comprehensive(
                    image_url=img_url,
                    selling_points=selling_points,
                    generate_angles=False  # DISABLED: Too expensive - generates 6 variations per image
                )
                
                # Get enhanced image (only one, not multiple variations)
                enhanced_url = enhancement_result.get("annotated_url") or \
                             enhancement_result.get("enhanced_url") or \
                             img_url
                enhanced_images.append(enhanced_url)
                enhanced_data.append(enhancement_result)
                
                logger.info(f"Successfully enhanced image {idx+1}")
                
            except Exception as e:
                logger.error(f"Failed to enhance image {idx+1}: {str(e)}", exc_info=True)
                # Fallback to original image if enhancement fails
                enhanced_images.append(img_url)
                enhanced_data.append({
                    "enhanced_url": img_url,
                    "angles": [img_url],
                    "annotated_url": None,
                    "error": str(e)
                })
        
        # Store enhancement metadata in job
        if not job.job_metadata:
            job.job_metadata = {}
        job.job_metadata["enhancements"] = enhanced_data
        
        job.progress = 20
        db.commit()
        logger.info(f"Image enhancement completed for job {job_id}")
        
        # Step 2: Generate storyboard with GPT-4
        logger.info(f"Starting storyboard generation for job {job_id}")
        storyboard_service = StoryboardService()
        try:
            storyboard = await storyboard_service.generate_storyboard(enhanced_images)
            
            # Extract selling points from storyboard for later use
            main_selling_points = storyboard.get("main_selling_points", [])
            
            # Update job metadata with storyboard
            if not job.job_metadata:
                job.job_metadata = {}
            job.job_metadata["storyboard"] = storyboard
            
            # If we didn't have selling points before, use the ones from storyboard
            # and enhance images again with annotations
            if main_selling_points and not any(data.get("annotated_url") for data in enhanced_data):
                logger.info(f"Re-enhancing images with storyboard selling points")
                for idx, img_url in enumerate(job.image_urls):
                    if idx < len(enhanced_data):
                        try:
                            enhanced_base = enhanced_data[idx].get("enhanced_url") or img_url
                            annotated = await enhancement_service.overlay_selling_points(
                                enhanced_base,
                                main_selling_points[:3]  # Limit to top 3 selling points
                            )
                            enhanced_data[idx]["annotated_url"] = annotated
                            enhanced_images[idx] = annotated
                        except Exception as e:
                            logger.warning(f"Failed to annotate image {idx+1} with selling points: {str(e)}")
                
                job.job_metadata["enhancements"] = enhanced_data
                db.commit()
            
            job.progress = 30
            db.commit()
            logger.info(f"Successfully generated storyboard for job {job_id}")
        except Exception as e:
            logger.error(f"Storyboard generation failed for job {job_id}: {str(e)}", exc_info=True)
            job.error_message = f"Storyboard generation failed: {str(e)}"
            job.status = JobStatus.FAILED
            db.commit()
            raise
        
        # Step 3: Generate videos with selected service
        # Get video service provider from job options (default to seedream)
        video_provider = job.options.get("video_provider", "seedream") if job.options else "seedream"
        logger.info(f"Using video provider: {video_provider} for job {job_id}")
        
        # Get the appropriate video service
        if video_provider == "seedream":
            video_service = SeedreamVideoService()
        elif video_provider == "openai":
            video_service = OpenAIVideoService()
        elif video_provider == "kling":
            video_service = KlingVideoService()
        elif video_provider == "veo3":
            video_service = Veo3VideoService()
        else:
            raise Exception(f"Unknown video provider: {video_provider}. Supported providers: seedream, openai, kling, veo3")
        
        video_clips = []
        
        # Check if videos already exist (from previous run that failed downstream)
        saved_videos = None
        if job.job_metadata and "video_clips" in job.job_metadata:
            saved_videos = job.job_metadata.get("video_clips")
            logger.info(f"Found saved video clips from previous run. Reusing to avoid wasting credits.")
        
        if saved_videos:
            # Use saved videos - skip generation to save credits
            video_clips = saved_videos
            logger.info(f"Reusing {len(video_clips)} saved video clips")
        else:
            # Generate new videos
            logger.info(f"Starting {video_provider} video generation for job {job_id}")
            
            total_videos = len(storyboard.get("shots", [])) * len(job.aspect_ratios)
            videos_generated = 0
            
            for i, shot in enumerate(storyboard.get("shots", [])):
                # Use enhanced image for this shot
                img_url = enhanced_images[i % len(enhanced_images)]
                prompt = shot.get("action_instructions", "Smooth product showcase")
                
                logger.info(f"Generating video for shot {i+1}/{len(storyboard.get('shots', []))}")
                
                # Generate video for each aspect ratio
                for aspect_ratio in job.aspect_ratios:
                    try:
                        logger.info(f"Generating video for shot {i+1}, aspect ratio {aspect_ratio} using {video_provider}")
                        video_url = await video_service.generate_video(
                            img_url,
                            prompt,
                            aspect_ratio=aspect_ratio
                        )
                        video_clips.append({
                            "shot": i,
                            "aspect_ratio": aspect_ratio,
                            "url": video_url,
                            "duration": shot.get("duration", 5)
                        })
                        videos_generated += 1
                        
                        # Save video URLs to job_metadata immediately after generation
                        # This prevents wasting credits if downstream steps fail
                        if not job.job_metadata:
                            job.job_metadata = {}
                        job.job_metadata["video_clips"] = video_clips
                        db.commit()
                        logger.info(f"Saved video URL to job metadata (shot {i+1}, {aspect_ratio})")
                        
                        # Update progress: 30% to 50% (20% range for video generation)
                        progress = 30 + int((videos_generated / total_videos) * 20)
                        job.progress = progress
                        db.commit()
                        logger.info(f"Video {videos_generated}/{total_videos} generated. Progress: {progress}%")
                    except Exception as e:
                        logger.error(f"Failed to generate video for shot {i+1}, aspect ratio {aspect_ratio}: {str(e)}", exc_info=True)
                        raise
            
            logger.info(f"{video_provider} video generation completed for job {job_id}. Saved {len(video_clips)} video URLs.")
        
        job.progress = 50
        db.commit()
        
        # Initialize storage service for saving intermediate results
        storage = StorageService()
        
        # Step 4: Generate voiceover
        # Check if voiceover already exists (from previous run that failed downstream)
        voiceover_path = None
        if job.job_metadata and "voiceover_saved" in job.job_metadata:
            # Voiceover was saved in previous run, download it
            saved_voiceover_url = job.job_metadata.get("voiceover_saved")
            logger.info(f"Found saved voiceover from previous run. Downloading from {saved_voiceover_url}")
            voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
            async with httpx.AsyncClient() as client:
                response = await client.get(saved_voiceover_url)
                with open(voiceover_path, "wb") as f:
                    f.write(response.content)
            logger.info(f"Reused saved voiceover to avoid wasting credits")
        else:
            # Generate new voiceover
            voice_service = ElevenLabsVoiceService()
            subtitle_text = " ".join([shot.get("text", "") for shot in storyboard.get("shots", [])])
            voiceover_audio = await voice_service.generate_voiceover(subtitle_text)
            
            # Save voiceover to temp file
            voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
            with open(voiceover_path, "wb") as f:
                f.write(voiceover_audio)
            
            # Save voiceover URL to job_metadata immediately after generation
            # Upload to storage so we can reuse it if downstream fails
            with open(voiceover_path, "rb") as f:
                voiceover_url = await storage.upload_file(
                    f,
                    f"voiceovers/{job.user_id}/{job.id}.mp3"
                )
                if not job.job_metadata:
                    job.job_metadata = {}
                job.job_metadata["voiceover_saved"] = voiceover_url
                db.commit()
                logger.info(f"Saved voiceover URL to job metadata to avoid re-generating if downstream fails")
        
        job.progress = 60
        db.commit()
        
        # Step 5: Select music
        music_selector = MusicSelector()
        music = music_selector.select_music(
            style=storyboard.get("music_style", "energetic"),
            duration=storyboard.get("total_duration", 30)
        )
        
        job.progress = 70
        db.commit()
        
        # Step 6: Process videos for each aspect ratio
        final_videos = {}
        
        for aspect_ratio in job.aspect_ratios:
            # Get clips for this aspect ratio
            clips_for_ratio = [c for c in video_clips if c["aspect_ratio"] == aspect_ratio]
            clip_urls = [c["url"] for c in clips_for_ratio]
            
            # Download clips
            clip_paths = []
            async with httpx.AsyncClient() as client:
                for clip_url in clip_urls:
                    clip_path = os.path.join(temp_dir, f"clip_{len(clip_paths)}.mp4")
                    response = await client.get(clip_url)
                    with open(clip_path, "wb") as f:
                        f.write(response.content)
                    clip_paths.append(clip_path)
            
            # Combine clips
            combined_path = os.path.join(temp_dir, f"combined_{aspect_ratio}.mp4")
            processor.combine_clips(clip_paths, combined_path)
            
            # Add subtitles
            subtitles = storyboard_service.generate_subtitles(storyboard)
            subtitled_path = os.path.join(temp_dir, f"subtitled_{aspect_ratio}.mp4")
            processor.add_subtitles(combined_path, subtitles, subtitled_path)
            
            # Add audio (voiceover + music)
            final_path = os.path.join(temp_dir, f"final_{aspect_ratio}.mp4")
            processor.add_audio(subtitled_path, voiceover_path, final_path, music.get("url"))
            
            # Resize to exact aspect ratio
            resized_path = os.path.join(temp_dir, f"resized_{aspect_ratio}.mp4")
            processor.resize_video(final_path, resized_path, aspect_ratio)
            
            # Upload to S3
            with open(resized_path, "rb") as f:
                video_url = await storage.upload_file(
                    f,
                    f"videos/{job.user_id}/{job.id}/{aspect_ratio}.mp4"
                )
                final_videos[aspect_ratio] = video_url
        
        job.progress = 90
        db.commit()
        
        # Step 7: Generate thumbnail
        thumbnail_path = os.path.join(temp_dir, "thumbnail.jpg")
        import ffmpeg
        if final_videos:
            first_video_url = list(final_videos.values())[0]
            # Download video for thumbnail extraction
            async with httpx.AsyncClient() as client:
                response = await client.get(first_video_url)
                temp_video = os.path.join(temp_dir, "temp_video.mp4")
                with open(temp_video, "wb") as f:
                    f.write(response.content)
            
            stream = ffmpeg.input(temp_video)
            stream = ffmpeg.output(stream, thumbnail_path, vframes=1)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            with open(thumbnail_path, "rb") as f:
                thumbnail_url = await storage.upload_file(
                    f,
                    f"thumbnails/{job.user_id}/{job.id}.jpg"
                )
        else:
            thumbnail_url = None
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.video_urls = final_videos
        job.thumbnail_url = thumbnail_url
        job.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        if 'job' in locals():
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        raise
    finally:
        # Cleanup
        processor.cleanup()
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        db.close()


@celery_app.task(bind=True, max_retries=0)
def process_video_job(self, job_id: str):
    """
    Main video generation workflow (Celery task wrapper)
    """
    logger.info(f"Celery task process_video_job started for job_id: {job_id}")
    try:
        asyncio.run(_process_video_job_async(job_id))
        logger.info(f"Celery task process_video_job completed for job_id: {job_id}")
    except Exception as e:
        logger.error(f"Celery task process_video_job failed for job_id: {job_id}, error: {str(e)}", exc_info=True)
        # Don't retry - let the job fail and user can retry manually
        raise

