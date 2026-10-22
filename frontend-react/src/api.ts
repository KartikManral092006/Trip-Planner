import type { Trip, TripRequest } from './types'

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

interface ValidationError {
  loc: (string | number)[]
  msg: string
}

export class ApiError extends Error {
  status: number
  messages: string[]

  constructor(status: number, messages: string[]) {
    super(messages.join(' '))
    this.name = 'ApiError'
    this.status = status
    this.messages = messages
  }
}

export function parseErrorDetail(detail: unknown): string[] {
  if (typeof detail === 'string') {
    return [detail]
  }
  if (Array.isArray(detail)) {
    return (detail as ValidationError[]).map((error) => {
      const field = error.loc.slice(1).join(' → ') || 'trip'
      return `${field}: ${error.msg.replace(/^Value error, /, '')}`
    })
  }
  return ['Something went wrong.']
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new ApiError(0, [`Cannot reach the API at ${API_URL}. Is it running?`])
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(response.status, parseErrorDetail(body.detail))
  }

  return response.json() as Promise<T>
}

interface StartedTrip {
  thread_id: string
  status: 'running'
}

export function createTrip(trip: TripRequest): Promise<StartedTrip> {
  return request('/trips', { method: 'POST', body: JSON.stringify(trip) })
}

export function getTrip(threadId: string, signal?: AbortSignal): Promise<Trip> {
  return request(`/trips/${threadId}`, { signal })
}

export function sendDecision(threadId: string, approved: boolean, feedback = ''): Promise<StartedTrip> {
  return request(`/trips/${threadId}/approval`, {
    method: 'POST',
    body: JSON.stringify({ approved, feedback }),
  })
}

export function retryTrip(threadId: string): Promise<StartedTrip> {
  return request(`/trips/${threadId}/retry`, { method: 'POST' })
}
