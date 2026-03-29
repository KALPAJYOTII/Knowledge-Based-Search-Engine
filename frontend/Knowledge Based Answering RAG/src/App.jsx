import { useState } from 'react'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [files, setFiles] = useState([])
  const [textInput, setTextInput] = useState('')
  const [query, setQuery] = useState('')
  const [uploadMessage, setUploadMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [retrievedChunks, setRetrievedChunks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFilesChange = (event) => {
    setFiles(Array.from(event.target.files))
  }

  const uploadFiles = async () => {
    if (!files.length) {
      setUploadMessage('Please select one or more PDF files to upload.')
      return
    }

    setLoading(true)
    setError('')
    setUploadMessage('Uploading files...')

    const results = []

    for (const file of files) {
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${process.env.BASE_URL}/api/documents/upload`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          const payload = await response.json()
          throw new Error(payload.detail || 'Upload failed')
        }

        const data = await response.json()
        results.push(`${data.filename}: ${data.chunks_created} chunks added`)
      } catch (err) {
        results.push(`${file.name}: ${err.message}`)
      }
    }

    setUploadMessage(results.join('\n'))
    setLoading(false)
  }

  const uploadText = async () => {
    if (!textInput.trim()) {
      setUploadMessage('Please enter text before uploading.')
      return
    }

    setLoading(true)
    setError('')
    setUploadMessage('Uploading text content...')

    try {
      const response = await fetch(`${process.env.BASE_URL}/api/documents/upload-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: 'text-input.txt',
          content: textInput,
          metadata: { source: 'text-input' },
        }),
      })

      if (!response.ok) {
        const payload = await response.json()
        throw new Error(payload.detail || 'Upload failed')
      }

      const data = await response.json()
      setUploadMessage(`Text upload succeeded: ${data.chunks_created} chunks added`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query.')
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setRetrievedChunks([])

    try {
      const response = await fetch(`${process.env.BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, top_k: 1 }),
      })

      if (!response.ok) {
        const payload = await response.json()
        throw new Error(payload.detail || 'Query failed')
      }

      const data = await response.json()
      setAnswer(data.answer)

      console.log('Query answer:', data)
      console.log('Retrieved chunks:', data.retrieved_chunks)
      setRetrievedChunks(data.retrieved_chunks || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <img src={heroImg} className="hero-image" alt="Hero" />
        <div>
          <h1>Knowledge-Based Search</h1>
          <p>Upload PDF(s) or text, store them in the vector database, then query the content.</p>
        </div>
      </header>

      <main className="app-main">
        <section className="upload-section">
          <h2>Upload PDF Files</h2>
          <input type="file" accept="application/pdf" multiple onChange={handleFilesChange} />
          <button onClick={uploadFiles} disabled={loading}>
            Upload Selected Files
          </button>

          <h2>Upload Text</h2>
          <textarea
            value={textInput}
            onChange={(event) => setTextInput(event.target.value)}
            placeholder="Paste text here to upload and index"
            rows={10}
          />
          <button onClick={uploadText} disabled={loading}>
            Upload Text
          </button>

          {uploadMessage && (
            <div className="status-message">
              <pre>{uploadMessage}</pre>
            </div>
          )}
        </section>

        <section className="query-section">
          <h2>Query Indexed Content</h2>
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask a question based on the uploaded content"
          />
          <button onClick={handleQuery} disabled={loading}>
            Run Query
          </button>

          {error && <div className="error-message">{error}</div>}
          {loading && <div className="loading-message">Working…</div>}

          {answer && (
            <div className="answer-box">
              <h3>Answer</h3>
              <p>{answer}</p>
            </div>
          )}

          {retrievedChunks.length > 0 && (
            <div className="results-box">
              <h3>Retrieved Chunks</h3>
              <ul>
                {retrievedChunks.map((chunk, index) => (
                  <li key={index}>
                    <strong>Score:</strong> {chunk.similarity_score?.toFixed(4)}<br />
                    <strong>Text:</strong> {chunk.chunk_text}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
