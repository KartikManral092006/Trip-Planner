import { useCallback, useState } from 'react'

const STORAGE_KEY = 'travel-planner-thread-id'

function readStored(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function writeStored(threadId: string | null): void {
  try {
    if (threadId) {
      localStorage.setItem(STORAGE_KEY, threadId)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    return
  }
}

export function useStoredThreadId(): [string | null, (threadId: string | null) => void] {
  const [threadId, setThreadIdState] = useState<string | null>(readStored)

  const setThreadId = useCallback((next: string | null) => {
    writeStored(next)
    setThreadIdState(next)
  }, [])

  return [threadId, setThreadId]
}
