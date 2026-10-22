import { useCallback, useEffect, useState } from 'react'

import { ApiError, getTrip } from '../api'
import type { Trip } from '../types'

export const POLL_MS = 4000
const RETRY_MS = 8000

interface UseTripResult {
  trip: Trip | null
  error: string | null
  notFound: boolean
  refresh: () => void
}

export function useTrip(threadId: string): UseTripResult {
  const [trip, setTrip] = useState<Trip | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [refreshCount, setRefreshCount] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    let timer: ReturnType<typeof setTimeout> | undefined

    async function load() {
      try {
        const next = await getTrip(threadId, controller.signal)
        setTrip(next)
        setError(null)
        if (next.status === 'running') {
          timer = setTimeout(load, POLL_MS)
        }
      } catch (caught) {
        if (controller.signal.aborted) {
          return
        }
        if (caught instanceof ApiError && caught.status === 404) {
          setNotFound(true)
          return
        }
        setError(caught instanceof Error ? caught.message : 'Could not load the trip.')
        timer = setTimeout(load, RETRY_MS)
      }
    }

    load()

    return () => {
      controller.abort()
      clearTimeout(timer)
    }
  }, [threadId, refreshCount])

  const refresh = useCallback(() => setRefreshCount((count) => count + 1), [])

  return { trip, error, notFound, refresh }
}
