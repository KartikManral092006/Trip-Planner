import { useState, type ChangeEvent } from 'react'

import { ApiError, sendDecision } from '../api'

interface ApprovalPanelProps {
  threadId: string
  onSent: () => void
}

export function ApprovalPanel({ threadId, onSent }: ApprovalPanelProps) {
  const [feedback, setFeedback] = useState('')
  const [sending, setSending] = useState(false)
  const [errors, setErrors] = useState<string[]>([])

  async function submit(approved: boolean) {
    setSending(true)
    setErrors([])
    try {
      await sendDecision(threadId, approved, approved ? '' : feedback.trim())
      onSent()
    } catch (caught) {
      setErrors(caught instanceof ApiError ? caught.messages : ['Could not send your decision.'])
      setSending(false)
    }
  }

  function handleFeedbackChange(event: ChangeEvent<HTMLTextAreaElement>) {
    setFeedback(event.target.value)
  }

  function handleApprove() {
    submit(true)
  }

  function handleRequestChanges() {
    submit(false)
  }

  return (
    <section className="card approval" aria-labelledby="approval-title">
      <h2 id="approval-title">Your decision</h2>
      <label>
        What should change?
        <textarea
          rows={3}
          value={feedback}
          onChange={handleFeedbackChange}
          maxLength={1000}
          placeholder="e.g. Find a cheaper hotel near King's Cross, or a direct flight"
        />
      </label>

      {errors.length > 0 && (
        <ul className="notice error" role="alert">
          {errors.map((message) => <li key={message}>{message}</li>)}
        </ul>
      )}

      <div className="actions">
        <button type="button" className="primary" onClick={handleApprove} disabled={sending}>
          Approve plan
        </button>
        <button
          type="button"
          onClick={handleRequestChanges}
          disabled={sending || feedback.trim() === ''}
        >
          Request changes
        </button>
      </div>
    </section>
  )
}
