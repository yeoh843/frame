'use client'

import { useState, useEffect } from 'react'
import { videoAPI } from '@/lib/api'
import ReactPlayer from 'react-player'
import ImageModal from './ImageModal'

interface Job {
  job_id: string
  status: string
  progress: number
  image_urls?: string[] | null
  video_urls: Record<string, string> | null
  thumbnail_url: string | null
  error_message: string | null
  job_metadata?: {
    video_clips?: Array<{
      shot: number
      aspect_ratio: string
      url: string
      duration: number
    }>
  } | null
  created_at: string
}

export default function VideoList() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  useEffect(() => {
    fetchJobs()
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchJobs, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchJobs = async () => {
    try {
      const data = await videoAPI.listJobs()
      setJobs(data)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'processing':
        return 'text-blue-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const handleDelete = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this job?')) return
    try {
      await videoAPI.deleteJob(jobId)
      fetchJobs()
    } catch (error) {
      alert('Failed to delete job')
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (jobs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Your Videos</h2>
        <p className="text-gray-600">No videos yet. Create your first video!</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Your Videos</h2>
      <div className="space-y-6">
        {jobs.map((job) => (
          <div key={job.job_id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="font-medium">Job #{job.job_id.slice(0, 8)}</p>
                <p className={`text-sm ${getStatusColor(job.status)}`}>
                  {job.status.toUpperCase()} {job.progress > 0 && `- ${job.progress}%`}
                </p>
                <p className="text-xs text-gray-500">
                  Created: {new Date(job.created_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => handleDelete(job.job_id)}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>

            {job.image_urls && job.image_urls.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium mb-2">Uploaded Images ({job.image_urls.length}):</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {job.image_urls.map((imageUrl, index) => (
                    <div
                      key={index}
                      className="relative aspect-square rounded-lg overflow-hidden border-2 border-gray-200 hover:border-blue-500 transition-colors cursor-pointer bg-gray-100"
                      onClick={() => setSelectedImage(imageUrl)}
                    >
                      <img
                        src={imageUrl}
                        alt={`Uploaded image ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Show video clips (intermediate results before processing) */}
            {job.job_metadata?.video_clips && job.job_metadata.video_clips.length > 0 && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm font-medium mb-2 text-blue-800">
                  🎬 Generated Video Clips (before processing) - {job.job_metadata.video_clips.length} clips
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {job.job_metadata.video_clips.map((clip: any, index: number) => (
                    <div key={index} className="bg-white rounded-lg p-2 border border-blue-300">
                      <p className="text-xs text-gray-600 mb-1">
                        Shot {clip.shot + 1} - {clip.aspect_ratio}
                      </p>
                      <div className="relative aspect-video bg-black rounded">
                        <ReactPlayer
                          url={clip.url}
                          controls
                          width="100%"
                          height="100%"
                          playing={false}
                        />
                      </div>
                      <a
                        href={clip.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline mt-1 inline-block"
                      >
                        Download
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {job.status === 'completed' && job.video_urls && (
              <div className="space-y-4 mt-4">
                {Object.entries(job.video_urls).map(([ratio, url]) => (
                  <div key={ratio} className="border rounded p-2">
                    <p className="text-sm font-medium mb-2">Aspect Ratio: {ratio}</p>
                    <ReactPlayer
                      url={url}
                      controls
                      width="100%"
                      height="auto"
                    />
                    <a
                      href={url}
                      download
                      className="inline-block mt-2 text-blue-600 hover:underline text-sm"
                    >
                      Download
                    </a>
                  </div>
                ))}
              </div>
            )}

            {job.status === 'processing' && (
              <div className="w-full bg-gray-200 rounded-full h-2.5 mt-4">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all"
                  style={{ width: `${job.progress}%` }}
                ></div>
              </div>
            )}

            {job.status === 'failed' && job.error_message && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-800 font-medium">Error:</p>
                <p className="text-sm text-red-600 mt-1">{job.error_message}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <ImageModal imageUrl={selectedImage} onClose={() => setSelectedImage(null)} />
    </div>
  )
}




