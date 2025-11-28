import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000'

// Check if backend is running on component mount
async function checkBackendHealth() {
  try {
    const response = await axios.get(`${API_BASE}/api/health`, { timeout: 5000 })
    return response.data
  } catch (error) {
    console.error('Backend health check failed:', error)
    return null
  }
}

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [progress, setProgress] = useState('')
  const [backendStatus, setBackendStatus] = useState(null)

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then(status => {
      setBackendStatus(status)
      if (!status) {
        setError('⚠️ Cannot connect to backend. Make sure the server is running on http://localhost:8000')
      } else if (!status.model_loaded) {
        setError('⚠️ Backend is running but model is still loading. Please wait...')
      }
    })
  }, [])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4', 'audio/ogg']
      const allowedExtensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
      const fileExt = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'))
      
      if (!allowedExtensions.includes(fileExt)) {
        setError(`Unsupported file type. Please upload: ${allowedExtensions.join(', ')}`)
        setFile(null)
        return
      }
      
      // Check file size (50MB limit)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File too large. Maximum size: 50MB')
        setFile(null)
        return
      }
      
      setFile(selectedFile)
      setError(null)
      setResult(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError(null)
    setProgress('Uploading file...')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      setProgress('Separating vocals and music (this may take a minute)...')
      
      const response = await axios.post(`${API_BASE}/api/separate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 900000, // 15 minutes - enough for full songs on CPU
        // Note: For production, consider implementing background jobs instead
      })

      if (response.data.status === 'success') {
        setResult(response.data)
        setProgress('')
      } else {
        throw new Error(response.data.message || 'Separation failed')
      }
    } catch (err) {
      console.error('Separation error:', err)
      
      let errorMessage = 'Failed to process audio. Please try again.'
      
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        errorMessage = '❌ Cannot connect to backend server. Make sure it\'s running on http://localhost:8000'
      } else if (err.response?.status === 404) {
        errorMessage = `❌ Endpoint not found: ${err.config?.url}. Check if backend is running.`
      } else if (err.response?.status === 500) {
        errorMessage = `❌ Server error: ${err.response?.data?.detail || 'Internal server error'}`
      } else if (err.response?.data?.detail) {
        errorMessage = `❌ ${err.response.data.detail}`
      } else if (err.message) {
        errorMessage = `❌ ${err.message}`
      }
      
      setError(errorMessage)
      setProgress('')
    } finally {
      setLoading(false)
    }
  }

  const getFileUrl = (filePath) => {
    // Handle both absolute and relative paths
    if (filePath.startsWith('http')) {
      return filePath
    }
    return `${API_BASE}${filePath.startsWith('/') ? '' : '/'}${filePath}`
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎤 Karaoke Generator</h1>
          <p className="subtitle">AI-powered source separation for perfect karaoke tracks</p>
          {backendStatus && (
            <div className={`backend-status ${backendStatus.model_loaded ? 'ready' : 'loading'}`}>
              {backendStatus.model_loaded ? '✅ Backend Ready' : '⏳ Model Loading...'}
            </div>
          )}
        </header>

        <main className="main-content">
          {!result ? (
            <form onSubmit={handleSubmit} className="upload-form">
              <div className="upload-area">
                <input
                  type="file"
                  id="file-input"
                  accept=".mp3,.wav,.flac,.m4a,.ogg"
                  onChange={handleFileChange}
                  className="file-input"
                  disabled={loading}
                />
                <label htmlFor="file-input" className="file-label">
                  {file ? (
                    <div className="file-selected">
                      <span className="file-icon">📁</span>
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                  ) : (
                    <div className="file-placeholder">
                      <span className="upload-icon">⬆️</span>
                      <span>Click to upload a song</span>
                      <span className="file-hint">
                        Supports: MP3, WAV, FLAC, M4A, OGG
                      </span>
                    </div>
                  )}
                </label>
              </div>

              {error && (
                <div className="error-message">
                  ⚠️ {error}
                </div>
              )}

              {progress && (
                <div className="progress-message">
                  {loading && <span className="spinner">⏳</span>}
                  {progress}
                </div>
              )}

              <button
                type="submit"
                className="submit-button"
                disabled={!file || loading}
              >
                {loading ? 'Processing...' : 'Generate Karaoke'}
              </button>
            </form>
          ) : (
            <div className="results">
              <div className="success-header">
                <h2>✨ Your karaoke is ready!</h2>
                {result.metadata && (
                  <p className="metadata">
                    Duration: {result.metadata.duration_seconds}s • 
                    Sample Rate: {result.metadata.sample_rate}Hz
                  </p>
                )}
              </div>

              <div className="audio-players">
                <div className="audio-card">
                  <h3>🎵 Karaoke Track (Music Only)</h3>
                  <audio controls src={getFileUrl(result.files.instrumental)}>
                    Your browser does not support the audio element.
                  </audio>
                  <a
                    href={getFileUrl(result.files.instrumental)}
                    download
                    className="download-button"
                  >
                    📥 Download Instrumental
                  </a>
                </div>

                <div className="audio-card">
                  <h3>🎤 Isolated Vocals</h3>
                  <audio controls src={getFileUrl(result.files.vocals)}>
                    Your browser does not support the audio element.
                  </audio>
                  <a
                    href={getFileUrl(result.files.vocals)}
                    download
                    className="download-button"
                  >
                    📥 Download Vocals
                  </a>
                </div>

                <div className="audio-card">
                  <h3>🔊 Original Song</h3>
                  <audio controls src={getFileUrl(result.files.original)}>
                    Your browser does not support the audio element.
                  </audio>
                  <a
                    href={getFileUrl(result.files.original)}
                    download
                    className="download-button"
                  >
                    📥 Download Original
                  </a>
                </div>
              </div>

              <button
                onClick={() => {
                  setResult(null)
                  setFile(null)
                  setError(null)
                }}
                className="new-upload-button"
              >
                🎵 Process Another Song
              </button>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>
            Powered by Demucs source separation • 
            Upload high-quality audio files for best results
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App

