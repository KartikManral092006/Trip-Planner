import { useCallback } from 'react'

import { ErrorBoundary } from './components/ErrorBoundary'
import { Landing } from './components/landing/Landing'
import { TripForm } from './components/TripForm'
import { TripView } from './components/TripView'
import { HOME_HREF, useHashRoute } from './hooks/useHashRoute'
import { useStoredThreadId } from './hooks/useStoredThreadId'

export default function App() {
  const route = useHashRoute()
  const [threadId, setThreadId] = useStoredThreadId()

  const startOver = useCallback(() => setThreadId(null), [setThreadId])

  if (route === 'home') {
    return <Landing hasTrip={threadId !== null} />
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1><a className="home-link" href={HOME_HREF}>AI Travel Planner</a></h1>
          <p className="muted">Agents research your trip, code checks the budget, and you approve the plan.</p>
        </div>
        {threadId && (
          <button type="button" onClick={startOver}>Plan another trip</button>
        )}
      </header>

      <main>
        <ErrorBoundary onReset={startOver}>
          {threadId ? (
            <TripView key={threadId} threadId={threadId} onNotFound={startOver} />
          ) : (
            <TripForm onCreated={setThreadId} />
          )}
        </ErrorBoundary>
      </main>
    </div>
  )
}
