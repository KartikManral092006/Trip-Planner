import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { makeTrip, mockFetch } from './test/fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('goes from the form to a plan and approves it', async () => {
    const { fetchMock, calls } = mockFetch([
      { method: 'POST', path: '/trips', status: 202, body: { thread_id: 'trip-1', status: 'running' } },
      { method: 'GET', path: '/trips/trip-1', body: makeTrip() },
      { method: 'POST', path: '/trips/trip-1/approval', status: 202, body: { thread_id: 'trip-1', status: 'running' } },
      { method: 'GET', path: '/trips/trip-1', body: makeTrip({ status: 'approved' }) },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)
    await user.click(screen.getAllByRole('link', { name: 'Plan a trip' })[0])
    await user.click(await screen.findByRole('button', { name: 'Plan my trip' }))

    expect(await screen.findByRole('heading', { name: 'Goa Getaway' })).toBeInTheDocument()
    expect(screen.getByText('Over by')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Flight Dehradun to Goa' })).toHaveAttribute('href', 'https://example.com/flight')

    await user.click(screen.getByRole('button', { name: 'Approve plan' }))

    expect(await screen.findByText('Plan approved.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Download itinerary/ })).toBeInTheDocument()
    expect(calls.find((call) => call.path.endsWith('/approval'))?.body).toEqual({ approved: true, feedback: '' })
  })

  it('sends feedback when requesting changes', async () => {
    localStorage.setItem('travel-planner-thread-id', 'trip-1')
    window.location.hash = '#/plan'
    const { fetchMock, calls } = mockFetch([
      { method: 'GET', path: '/trips/trip-1', body: makeTrip() },
      { method: 'POST', path: '/trips/trip-1/approval', status: 202, body: { thread_id: 'trip-1', status: 'running' } },
      { method: 'GET', path: '/trips/trip-1', body: makeTrip({ status: 'running', next_steps: ['rerun_accommodation'] }) },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)
    const requestChanges = await screen.findByRole('button', { name: 'Request changes' })
    expect(requestChanges).toBeDisabled()

    await user.type(screen.getByLabelText('What should change?'), 'Find a cheaper hotel')
    await user.click(requestChanges)

    expect(await screen.findByText(/Finding new places to stay/)).toBeInTheDocument()
    expect(calls.find((call) => call.path.endsWith('/approval'))?.body).toEqual({
      approved: false,
      feedback: 'Find a cheaper hotel',
    })
  })

  it('offers a retry when the planner failed', async () => {
    localStorage.setItem('travel-planner-thread-id', 'trip-1')
    window.location.hash = '#/plan'
    const { fetchMock, calls } = mockFetch([
      { method: 'GET', path: '/trips/trip-1', body: makeTrip({ status: 'failed', error: 'Rate limit reached', itinerary: null }) },
      { method: 'POST', path: '/trips/trip-1/retry', status: 202, body: { thread_id: 'trip-1', status: 'running' } },
      { method: 'GET', path: '/trips/trip-1', body: makeTrip({ status: 'running', next_steps: ['synthesizer'] }) },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)
    expect(await screen.findByText('Rate limit reached')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Retry' }))

    expect(await screen.findByText(/Writing the itinerary/)).toBeInTheDocument()
    expect(calls.some((call) => call.path.endsWith('/retry'))).toBe(true)
  })

  it('returns to the form when the trip no longer exists', async () => {
    localStorage.setItem('travel-planner-thread-id', 'gone')
    window.location.hash = '#/plan'
    const { fetchMock } = mockFetch([
      { method: 'GET', path: '/trips/gone', status: 404, body: { detail: 'Trip not found.' } },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)
    await user.click(await screen.findByRole('button', { name: 'Plan a new trip' }))

    expect(screen.getByRole('button', { name: 'Plan my trip' })).toBeInTheDocument()
  })
})
