import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function App() {
  const [file, setFile]           = useState(null)
  const [jd, setJd]               = useState('')
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState('')

  async function handleSubmit() {
    if (!file || !jd.trim()) {
      setError('Please upload a resume and paste a job description.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('resume', file)
    formData.append('job_description', jd)

    try {
      const res = await axios.post(`${API}/screen`, formData)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>Resume Screener</h1>
      <p style={styles.sub}>AI-powered resume vs job description matcher</p>
      <InputPanel file={file} setFile={setFile} jd={jd} setJd={setJd}
        onSubmit={handleSubmit} loading={loading} />
      {error && <p style={styles.error}>{error}</p>}
      {result && <ResultPanel result={result} />}
    </div>
  )
}
function InputPanel({ file, setFile, jd, setJd, onSubmit, loading }) {
  return (
    <div style={styles.card}>
      <div style={styles.section}>
        <label style={styles.label}>Upload Resume (PDF or DOCX)</label>
        <input type="file" accept=".pdf,.docx"
          onChange={e => setFile(e.target.files[0])}
          style={styles.fileInput} />
        {file && <p style={styles.fileName}>✓ {file.name}</p>}
      </div>

      <div style={styles.section}>
        <label style={styles.label}>Job Description</label>
        <textarea
          value={jd}
          onChange={e => setJd(e.target.value)}
          placeholder="Paste the full job description here..."
          style={styles.textarea}
          rows={8}
        />
      </div>

      <button onClick={onSubmit} disabled={loading} style={styles.button}>
        {loading ? 'Analysing...' : 'Screen Resume'}
      </button>
    </div>
  )
}
function ResultPanel({ result }) {
  const gradeColors = {
    green: '#22c55e', blue: '#3b82f6',
    yellow: '#eab308', orange: '#f97316', red: '#ef4444'
  }
  const color = gradeColors[result.color] || '#888'

  return (
    <div style={styles.card}>
      <div style={{...styles.scoreBox, borderColor: color}}>
        <div style={{...styles.grade, color}}>{result.grade}</div>
        <div style={styles.scoreNum}>{result.final_score}%</div>
        <div style={styles.scoreLabel}>{result.label}</div>
      </div>

      <div style={styles.row}>
        <Stat label="Semantic" value={result.semantic_score} />
        <Stat label="Keywords" value={result.keyword_score} />
      </div>

      <SkillList title="✓ Matched Skills" skills={result.matched_skills} color="#22c55e" />
      <SkillList title="✗ Missing Skills" skills={result.missing_skills} color="#ef4444" />

      <div style={styles.recommendation}>
        <strong>Recommendation</strong>
        <p style={{margin: '6px 0 0', fontSize: '14px', lineHeight: '1.6'}}>
          {result.recommendation}
        </p>
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div style={styles.stat}>
      <div style={styles.statVal}>{value}%</div>
      <div style={styles.statLabel}>{label}</div>
    </div>
  )
}

function SkillList({ title, skills, color }) {
  if (!skills?.length) return null
  return (
    <div style={styles.section}>
      <label style={{...styles.label, color}}>{title}</label>
      <div style={styles.chips}>
        {skills.map((s, i) => (
          <span key={i} style={{...styles.chip, borderColor: color, color}}>{s}</span>
        ))}
      </div>
    </div>
  )
}
const styles = {
  page:   { maxWidth: '680px', margin: '0 auto', padding: '40px 20px',
            fontFamily: 'system-ui, sans-serif' },
  title:  { fontSize: '28px', fontWeight: '700', margin: '0 0 6px' },
  sub:    { fontSize: '14px', color: '#888', margin: '0 0 28px' },
  card:   { background: '#fff', border: '1px solid #e5e7eb',
            borderRadius: '12px', padding: '24px', marginBottom: '20px',
            boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  section:  { marginBottom: '18px' },
  label:    { fontSize: '13px', fontWeight: '600', display: 'block', marginBottom: '8px' },
  fileInput:{ width: '100%', padding: '10px', borderRadius: '8px',
              border: '1px solid #e5e7eb', fontSize: '13px' },
  fileName: { fontSize: '13px', color: '#22c55e', margin: '6px 0 0' },
  textarea: { width: '100%', padding: '10px', borderRadius: '8px',
              border: '1px solid #e5e7eb', fontSize: '13px',
              resize: 'vertical', boxSizing: 'border-box' },
  button:   { width: '100%', padding: '12px', background: '#111',
              color: '#fff', border: 'none', borderRadius: '8px',
              fontSize: '15px', fontWeight: '600', cursor: 'pointer' },
  error:    { color: '#ef4444', fontSize: '13px', margin: '0 0 16px' },
  scoreBox: { textAlign: 'center', padding: '20px', borderRadius: '10px',
              border: '2px solid', marginBottom: '20px' },
  grade:    { fontSize: '48px', fontWeight: '800', lineHeight: 1 },
  scoreNum: { fontSize: '28px', fontWeight: '700', margin: '4px 0' },
  scoreLabel:{ fontSize: '14px', color: '#888' },
  row:      { display: 'flex', gap: '12px', marginBottom: '18px' },
  stat:     { flex: 1, background: '#f9fafb', borderRadius: '8px',
              padding: '12px', textAlign: 'center' },
  statVal:  { fontSize: '22px', fontWeight: '700' },
  statLabel:{ fontSize: '12px', color: '#888', marginTop: '2px' },
  chips:    { display: 'flex', flexWrap: 'wrap', gap: '6px' },
  chip:     { fontSize: '12px', padding: '3px 10px', borderRadius: '99px',
              border: '1px solid' },
  recommendation: { background: '#f9fafb', borderRadius: '8px',
                    padding: '14px', fontSize: '13px' }
}
