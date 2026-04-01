import { useState } from 'react'
import './App.css'

function UploadIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3v10m0 0l-3-3m3 3l3-3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 15.5V18a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-2.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="6" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <path d="m16.5 16.5 3.5 3.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15 3v5h5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9 12h6M9 16h3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

function SparkleIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2.5l1.57 3.18 3.52.51-2.55 2.49.61 3.52L12 11.18l-3.15 1.65.61-3.52L7 6.19l3.52-.51L12 2.5Z" fill="currentColor" />
    </svg>
  )
}

function Card({ children, className = '' }) {
  return <section className={`card ${className}`}>{children}</section>
}

function Button({ children, variant = 'primary', className = '', ...props }) {
  return (
    <button className={`button button-${variant} ${className}`} {...props}>
      {children}
    </button>
  )
}

function Input(props) {
  return <input className="field field-input" {...props} />
}

function Textarea(props) {
  return <textarea className="field field-textarea" {...props} />
}

function Spinner() {
  return <div className="spinner" aria-label="Loading" />
}

function App() {
  const rawBaseUrl = import.meta.env.VITE_BASE_URL || ''
  const BASE_URL = rawBaseUrl.replace(/\/+$/, '')
  const [files, setFiles] = useState([])
  const [textInput, setTextInput] = useState('')
  const [query, setQuery] = useState('')
  const [uploadMessage, setUploadMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [retrievedChunks, setRetrievedChunks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)

  const readResponseText = async (response) => {
    try {
      return await response.clone().text()
    } catch {
      return ''
    }
  }

  const parseJsonResponse = async (response) => {
    const text = await readResponseText(response)
    if (!text) return null
    try {
      return JSON.parse(text)
    } catch {
      return null
    }
  }

  const getResponseErrorMessage = async (response, defaultMessage) => {
    const payload = await parseJsonResponse(response)
    if (payload?.detail) return payload.detail
    if (payload && typeof payload === 'object') return JSON.stringify(payload)

    const rawText = await readResponseText(response)
    if (rawText) return rawText

    return `${response.status} ${response.statusText || defaultMessage} (${response.url})`
  }

  const buildUrl = (endpoint) => {
    return BASE_URL ? `${BASE_URL}${endpoint}` : endpoint
  }

  const handleFilesChange = (event) => {
    setFiles(Array.from(event.target.files))
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    setDragActive(true)
  }

  const handleDragLeave = () => {
    setDragActive(false)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setDragActive(false)
    setFiles(Array.from(event.dataTransfer.files))
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

        const response = await fetch(buildUrl('/api/documents/upload'), {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          const message = await getResponseErrorMessage(response, 'Upload failed')
          throw new Error(message)
        }

        const data = await parseJsonResponse(response)
        results.push(`${data?.filename || file.name}: ${data?.chunks_created ?? 'unknown'} chunks added`)
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
      const response = await fetch(buildUrl('/api/documents/upload-text'), {
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
        const message = await getResponseErrorMessage(response, 'Upload failed')
        throw new Error(message)
      }

      const data = await parseJsonResponse(response)
      setUploadMessage(`Text upload succeeded: ${data?.chunks_created ?? 'unknown'} chunks added`)
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
      const response = await fetch(buildUrl('/api/query'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, top_k: 1 }),
      })

      if (!response.ok) {
        const message = await getResponseErrorMessage(response, 'Query failed')
        throw new Error(message)
      }

      const data = await parseJsonResponse(response)
      if (!data) {
        throw new Error('No valid response returned from query')
      }

      setAnswer(data.answer)
      setRetrievedChunks(data.retrieved_chunks || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fileLabel = files.length ? files.map((file) => file.name).join(', ') : 'No files selected yet'

  return (
    <div className="page-shell">
      <div className="page-intro">
        <div className="brand-bar">
          <div className="brand-mark">
            <SearchIcon />
          </div>
          <div>
            <p className="eyebrow">Knowledge-Based Search</p>
            <h1 className='text-3xl'>Search documents with AI-powered retrieval</h1>
            <p className="hero-copy">
              Upload PDFs or paste text content, then ask natural language questions against your indexed data.
              Built for fast answers, clear sources, and a polished search experience.
            </p>
          </div>
        </div>

        <div className="hero-features">
          <div className="feature-card">
            <p className="feature-title">Upload or paste text</p>
            <p>Ingest documents and content quickly without complex setup.</p>
          </div>
          <div className="feature-card">
            <p className="feature-title">Ask any question</p>
            <p>Use natural language queries to explore your knowledge base.</p>
          </div>
          <div className="feature-card">
            <p className="feature-title">See source-backed answers</p>
            <p>Review answers with supporting document snippets and confidence.</p>
          </div>
        </div>
      </div>

      <main className="grid-layout">
        <Card>
          <div className="section-header">
            <div>
              <p className="section-label">Upload</p>
              <h2>Ingest files and text</h2>
            </div>
            <span className="status-pill">PDF + text ready</span>
          </div>

          <div
            className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <UploadIcon />
            <div>
              <p className="drop-title">Drag & drop documents here</p>
              <p className="drop-copy">Drop PDFs to upload them for semantic search indexing.</p>
            </div>
            <p className="drop-note">{fileLabel}</p>
            <input
              type="file"
              accept="application/pdf"
              multiple
              className="file-input"
              onChange={handleFilesChange}
            />
          </div>

          <div className="button-row">
            <Button type="button" onClick={uploadFiles} disabled={loading}>
              Upload PDF
            </Button>
            <Button type="button" variant="secondary" onClick={uploadText} disabled={loading}>
              Upload Text
            </Button>
          </div>

          <div className="field-group">
            <label className="field-label" htmlFor="text-upload">
              Paste text to index
            </label>
            <Textarea
              id="text-upload"
              value={textInput}
              onChange={(event) => setTextInput(event.target.value)}
              placeholder="Paste your notes, summaries, or document content here..."
              rows={6}
            />
          </div>

          {uploadMessage && (
            <div className="message-card message-info">
              <p>{uploadMessage}</p>
            </div>
          )}
        </Card>

        <div className="right-column">
          <Card>
            <div className="section-header">
              <div>
                <p className="section-label">Query</p>
                <h2>Ask your knowledge base</h2>
              </div>
            </div>
            <div className="query-row">
              <Input
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ask a question about your uploaded content"
              />
              <Button type="button" onClick={handleQuery} disabled={loading}>
                <SearchIcon />
                Search
              </Button>
            </div>
            {error && <div className="message-card message-error">{error}</div>}
            {loading && (
              <div className="status-row">
                <Spinner />
                <span>Searching your knowledge base</span>
              </div>
            )}
          </Card>

          <Card className="results-card">
            <div className="section-header">
              <div>
                <p className="section-label">Results</p>
                <h2>Answer & sources</h2>
              </div>
            </div>
            {answer ? (
              <div className="result-box">
                <p className="result-title">Answer</p>
                <p>{answer}</p>
              </div>
            ) : (
              <div className="empty-state">
                <p>Ask a question to see the answer and supporting document snippets.</p>
              </div>
            )}
            {retrievedChunks.length > 0 && (
              <div className="reference-list">
                {retrievedChunks.map((chunk, index) => (
                  <div key={index} className="reference-card">
                    <p className="reference-score">Score: {chunk.similarity_score?.toFixed(4)}</p>
                    <p>{chunk.chunk_text}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </main>
    </div>
  )
}

export default App
