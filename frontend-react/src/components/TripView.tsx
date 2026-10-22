import { useState } from 'react'

import { ApiError, retryTrip } from '../api'
import { useTrip } from '../hooks/useTrip'
import type { Trip } from '../types'
import { ApprovalPanel } from './ApprovalPanel'
import { BudgetTable } from './BudgetTable'
import { ItineraryView } from './ItineraryView'
import { ReviewNotes } from './ReviewNotes'
import { TripProgress } from './TripProgress'

function downloadMarkdown(markdown: string) {
  const url = URL.createObjectURL(new Blob([markdown], { type: 'text/markdown' }))
  const link = document.createElement('a')
  link.href = url
  link.download = 'itinerary.md'
  link.click()
  URL.revokeObjectURL(url)
}

interface FailedTripProps {
  trip: Trip
  onRetried: () => void
}

function FailedTrip({ trip, onRetried }: FailedTripProps) {
  const [retrying, setRetrying] = useState(false)
  const [retryError, setRetryError] = useState<string | null>(null)

  async function handleRetry() {
    setRetrying(true)
    setRetryError(null)
    try {
      await retryTrip(trip.thread_id)
      onRetried()
    } catch (caught) {
      setRetryError(caught instanceof ApiError ? caught.message : 'Retry failed.')
      setRetrying(false)
    }
  }

  return (
    <section className="card notice error" role="alert">
      <h2>The planner stopped</h2>
      <p>{trip.error}</p>
      <p className="muted">Progress is saved after every step, so a retry continues where it stopped.</p>
      {retryError && <p>{retryError}</p>}
      <button type="button" className="primary" onClick={handleRetry} disabled={retrying}>
        {retrying ? 'Retrying…' : 'Retry'}
      </button>
    </section>
  )
}

interface TripViewProps {
  threadId: string
  onNotFound: () => void
}

export function TripView({ threadId, onNotFound }: TripViewProps) {
  const { trip, error, notFound, refresh } = useTrip(threadId)

  if (notFound) {
    return (
      <section className="card notice warning" role="alert">
        <h2>This trip no longer exists.</h2>
        <button type="button" onClick={onNotFound}>Plan a new trip</button>
      </section>
    )
  }

  if (!trip) {
    return (
      <section className="card" aria-busy="true">
        <p>{error ?? 'Loading your trip…'}</p>
      </section>
    )
  }

  const currency = trip.trip.currency ?? 'INR'
  const finished = trip.status === 'approved' || trip.status === 'rejected'

  function handleDownload() {
    if (trip?.itinerary_markdown) {
      downloadMarkdown(trip.itinerary_markdown)
    }
  }

  return (
    <div className="trip">
      <p className="route">
        {trip.trip.origin} → {trip.trip.destination}
        <span className="muted"> · {trip.trip.travelers} traveler{trip.trip.travelers === 1 ? '' : 's'}</span>
      </p>

      {error && <p className="notice warning" role="status">{error} Retrying…</p>}

      {trip.status === 'running' && (
        <TripProgress
          nextSteps={trip.next_steps}
          revisions={trip.revisions}
          feedbackRounds={trip.feedback_rounds}
        />
      )}

      {trip.status === 'failed' && <FailedTrip trip={trip} onRetried={refresh} />}

      {trip.status === 'approved' && <p className="notice success" role="status">Plan approved.</p>}
      {trip.status === 'rejected' && <p className="notice warning" role="status">Plan rejected.</p>}

      {trip.status !== 'running' && trip.itinerary && trip.budget_summary && (
        <>
          <div className="plan">
            <ItineraryView itinerary={trip.itinerary} />
            <aside>
              <BudgetTable budget={trip.budget_summary} currency={currency} />
              <ReviewNotes ruleIssues={trip.rule_issues} evaluationFeedback={trip.evaluation_feedback} />
            </aside>
          </div>

          {trip.status === 'waiting_for_approval' && (
            <ApprovalPanel threadId={trip.thread_id} onSent={refresh} />
          )}

          {finished && trip.itinerary_markdown && (
            <button type="button" onClick={handleDownload}>Download itinerary (Markdown)</button>
          )}
        </>
      )}
    </div>
  )
}
