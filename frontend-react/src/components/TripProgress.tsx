const STEP_LABELS: Record<string, string> = {
  planner: 'Planning the research',
  transport_researcher: 'Researching transport',
  accommodation_researcher: 'Researching places to stay',
  activities_researcher: 'Researching activities and food',
  budget_calculator: 'Calculating the budget',
  synthesizer: 'Writing the itinerary',
  rule_checks: 'Checking the plan',
  llm_evaluator: 'Reviewing quality',
  reviser: 'Revising the plan',
  human_approval: 'Preparing the plan for you',
  feedback_router: 'Reading your feedback',
  rerun_transport: 'Finding new transport options',
  rerun_accommodation: 'Finding new places to stay',
  rerun_activities: 'Finding new activities',
  finalize: 'Finishing',
}

interface TripProgressProps {
  nextSteps: string[]
  revisions: number
  feedbackRounds: number
}

export function TripProgress({ nextSteps, revisions, feedbackRounds }: TripProgressProps) {
  const labels = nextSteps.map((step) => STEP_LABELS[step] ?? step)

  return (
    <section className="card progress" aria-live="polite" aria-busy="true">
      <div className="spinner" aria-hidden="true" />
      <div>
        <h2>{labels.length > 0 ? labels.join(' · ') : 'Starting'}…</h2>
        <p className="muted">
          Agents are researching and checking your plan. On the free tier this takes a few minutes.
        </p>
        {(revisions > 0 || feedbackRounds > 0) && (
          <p className="muted small">
            Automatic revisions: {revisions} · Your feedback rounds: {feedbackRounds}
          </p>
        )}
      </div>
    </section>
  )
}
