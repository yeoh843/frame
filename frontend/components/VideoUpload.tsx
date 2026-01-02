'use client'

import { useState, useMemo } from 'react'
import { useDropzone } from 'react-dropzone'
import { videoAPI } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import ImageModal from './ImageModal'

export default function VideoUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [aspectRatio, setAspectRatio] = useState<string>('9:16') // Single aspect ratio selection
  const [videoProvider, setVideoProvider] = useState<string>('seedream') // Video service provider selection
  const [uploading, setUploading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const { user } = useAuthStore()

  const imagePreviews = useMemo(() => {
    return files.map(file => URL.createObjectURL(file))
  }, [files])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    onDrop: (acceptedFiles, rejectedFiles) => {
      console.log('Dropzone onDrop triggered!')
      console.log('Accepted files:', acceptedFiles.length, acceptedFiles.map(f => f.name))
      if (rejectedFiles.length > 0) {
        console.warn('Rejected files:', rejectedFiles.map(f => ({ file: f.file.name, errors: f.errors })))
        setErrorMessage(`Some files were rejected. Please use PNG, JPG, or JPEG format.`)
        setTimeout(() => setErrorMessage(null), 5000)
      }
      if (acceptedFiles.length > 0) {
        // Replace files instead of appending (user wants only the new selection)
        setFiles(acceptedFiles.slice(0, 10)) // Keep max 10 files
        console.log('Files state updated. Total files:', acceptedFiles.length)
      } else {
        console.warn('No accepted files in onDrop')
      }
    },
    maxFiles: 10,
    multiple: true
  })

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    // Revoke the object URL to free memory
    URL.revokeObjectURL(imagePreviews[index])
  }

  const handleUpload = async () => {
    console.log('handleUpload called, files.length:', files.length, 'files:', files)
    if (files.length === 0) {
      console.warn('No files selected, aborting upload')
      setErrorMessage('Please select at least one image')
      setTimeout(() => setErrorMessage(null), 3000)
      return
    }
    
    console.log('Starting upload process...')
    setUploading(true)
    setSuccessMessage(null)
    setErrorMessage(null)
      try {
      console.log('Starting video generation with', files.length, 'images')
      console.log('Aspect ratio:', aspectRatio)
      console.log('Video provider:', videoProvider)
      const job = await videoAPI.createJob(files, [aspectRatio], videoProvider) // Send as array with single value
      console.log('Job created successfully:', job)
      setJobId(job.job_id)
      // Clean up object URLs
      imagePreviews.forEach(url => URL.revokeObjectURL(url))
      setFiles([])
      setSuccessMessage('Video generation started! Check the job list for progress.')
      setTimeout(() => setSuccessMessage(null), 5000)
    } catch (error: any) {
      console.error('Video generation error:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code,
        name: error.name,
        hasResponse: !!error.response,
        responseStatus: error.response?.status
      })
      
      let errorMsg = 'Upload failed'
      
      // Check if we got a response from the server
      if (error.response) {
        // Server responded - this is NOT a network error
        console.log('Server responded with status:', error.response.status)
        if (error.response.status === 401) {
          errorMsg = 'Authentication failed. Please log in again.'
          localStorage.removeItem('access_token')
          setTimeout(() => window.location.href = '/login', 2000)
        } else if (error.response.status === 0) {
          errorMsg = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          // Extract error message from FastAPI response
          const detail = error.response?.data?.detail
          if (Array.isArray(detail)) {
            // FastAPI validation errors are arrays of objects
            errorMsg = detail.map((err: any) => {
              const loc = Array.isArray(err.loc) ? err.loc.slice(1).join('.') : ''
              return `${loc ? loc + ': ' : ''}${err.msg || JSON.stringify(err)}`
            }).join(', ')
          } else if (typeof detail === 'string') {
            errorMsg = detail
          } else if (detail && typeof detail === 'object') {
            errorMsg = JSON.stringify(detail)
          } else {
            errorMsg = error.message || 'Upload failed'
          }
        }
      } else {
        // No response from server - this could be a real network error
        console.log('No response from server. Error code:', error.code, 'Message:', error.message)
        if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error') || error.message?.includes('Failed to fetch') || error.code === 'ECONNREFUSED') {
          errorMsg = 'Network error: Cannot connect to backend server. Please check if the backend is running on http://localhost:8000'
        } else {
          errorMsg = error.message || 'Upload failed. Please check console for details.'
        }
      }
      
      console.error('Final error message to display:', errorMsg)
      setErrorMessage(errorMsg)
      setTimeout(() => setErrorMessage(null), 8000)
    } finally {
      setUploading(false)
    }
  }

  const selectAspectRatio = (ratio: string) => {
    setAspectRatio(ratio)
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Create New Video</h2>
      
      {successMessage && (
        <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {successMessage}
        </div>
      )}
      
      {errorMessage && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {errorMessage}
        </div>
      )}
      
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Credits: {user?.credits || 0}</p>
        <p className="text-xs text-gray-500">Debug: {files.length} file(s) selected</p>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
      >
        <input {...getInputProps()} />
        <p className="text-gray-600">
          {isDragActive
            ? 'Drop images here...'
            : 'Drag & drop product images here, or click to select'}
        </p>
        <p className="text-sm text-gray-400 mt-2">Click to select multiple images at once (Max 10: PNG, JPG, JPEG)</p>
        {files.length > 0 && (
          <p className="text-sm text-green-600 mt-2 font-medium">
            {files.length} file(s) selected
          </p>
        )}
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium mb-3">Selected images ({files.length}):</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {files.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 hover:border-blue-500 transition-colors cursor-pointer bg-gray-100">
                  <img
                    src={imagePreviews[index]}
                    alt={file.name}
                    className="w-full h-full object-cover"
                    onClick={() => setSelectedImage(imagePreviews[index])}
                  />
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  title="Remove image"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <p className="text-xs text-gray-600 mt-1 truncate" title={file.name}>
                  {file.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6">
        <p className="text-sm font-medium mb-2">Aspect Ratio (Select One):</p>
        <div className="flex gap-2">
          {['9:16', '1:1', '16:9'].map((ratio) => (
            <button
              key={ratio}
              type="button"
              onClick={() => selectAspectRatio(ratio)}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                aspectRatio === ratio
                  ? 'bg-blue-600 text-white ring-2 ring-blue-400'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {ratio}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <p className="text-sm font-medium mb-2">Video Service Provider:</p>
        <select
          value={videoProvider}
          onChange={(e) => setVideoProvider(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="seedream">Seedream</option>
          <option value="openai">OpenAI (Sora)</option>
          <option value="kling">Kling AI</option>
          <option value="veo3">Veo3 (Google)</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">Select the video generation service to use</p>
      </div>

      <button
        onClick={(e) => {
          e.preventDefault()
          console.log('Button clicked! files.length:', files.length, 'uploading:', uploading)
          handleUpload()
        }}
        disabled={files.length === 0 || uploading}
        className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {uploading ? 'Uploading...' : `Generate Video${files.length > 0 ? ` (${files.length} image${files.length > 1 ? 's' : ''})` : ''}`}
      </button>

      <ImageModal imageUrl={selectedImage} onClose={() => setSelectedImage(null)} />
    </div>
  )
}




