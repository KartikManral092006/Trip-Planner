interface ReviewNotesProps {
  ruleIssues: string[]
  evaluationFeedback: string
}

export function ReviewNotes({ ruleIssues, evaluationFeedback }: ReviewNotesProps) {
  if (ruleIssues.length === 0 && !evaluationFeedback) {
    return null
  }

  return (
    <details className="card review-notes">
      <summary>Review notes</summary>
      <ul>
        {ruleIssues.map((issue) => <li key={issue}>Code check: {issue}</li>)}
        {evaluationFeedback && <li>Reviewer: {evaluationFeedback}</li>}
      </ul>
    </details>
  )
}
