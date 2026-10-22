import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { mockFetch } from '../test/fixtures'
import { TripForm } from './TripForm'

afterEach(() => {
  vi.unstubAllGlobals()
})

function renderForm() {
  const onCreated = vi.fn()
  render(<TripForm onCreated={onCreated} />)
  return { onCreated, user: userEvent.setup() }
}

describe('TripForm', () => {
  it('sends the trip with the choices made in the form', async () => {
    const { fetchMock, calls } = mockFetch([
      { method: 'POST', path: '/trips', status: 202, body: { thread_id: 'abc', status: 'running' } },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const { onCreated, user } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Add a traveler' }))
    await user.click(screen.getByRole('button', { name: 'Remove food' }))
    await user.type(screen.getByRole('textbox', { name: 'Add an interest' }), 'Hiking{Enter}')
    await user.click(screen.getByRole('button', { name: 'Bus' }))
    await user.click(screen.getByRole('radio', { name: 'Relaxed' }))
    await user.click(screen.getByRole('button', { name: 'Plan my trip' }))

    expect(onCreated).toHaveBeenCalledWith('abc')
    const body = calls[0].body as Record<string, unknown>
    expect(body).toMatchObject({
      origin: 'India',
      destination: 'UK',
      travelers: 3,
      budget: 240000,
      currency: 'INR',
      pace: 'relaxed',
      interests: ['museums', 'history', 'hiking'],
      transport_preference: ['flight', 'bus'],
    })
  })

  it('swaps the start and destination', async () => {
    const { user } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Swap start and destination' }))

    expect(screen.getByLabelText('From')).toHaveValue('UK')
    expect(screen.getByLabelText('To')).toHaveValue('India')
  })

  it('updates the live ticket as the form changes', async () => {
    const { user } = renderForm()
    const ticket = screen.getByRole('complementary', { name: 'Trip summary' })

    expect(ticket).toHaveTextContent('India → UK')
    expect(ticket).toHaveTextContent('About ₹17,143 per person a day')

    await user.click(screen.getByRole('button', { name: 'Add a traveler' }))
    expect(ticket).toHaveTextContent('About ₹11,429 per person a day')

    await user.clear(screen.getByLabelText('To'))
    await user.type(screen.getByLabelText('To'), 'Scotland')
    expect(ticket).toHaveTextContent('India → Scotland')
  })

  it('adds a suggested interest with one click', async () => {
    const { user } = renderForm()

    await user.click(screen.getByRole('button', { name: 'beaches' }))

    expect(screen.getByRole('button', { name: 'Remove beaches' })).toBeInTheDocument()
  })

  it('keeps at least one transport mode selected', async () => {
    const { user } = renderForm()
    const flight = screen.getByRole('button', { name: 'Flight' })

    await user.click(flight)

    expect(flight).toHaveAttribute('aria-pressed', 'true')
  })

  it('explains what to fix before calling the API', async () => {
    const fetchSpy = vi.fn()
    vi.stubGlobal('fetch', fetchSpy)
    const { user } = renderForm()

    await user.clear(screen.getByLabelText('From'))
    await user.clear(screen.getByLabelText('Total budget'))
    await user.click(screen.getByRole('button', { name: 'Plan my trip' }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Add where you are starting from.')
    expect(alert).toHaveTextContent('Enter a budget above zero.')
    expect(fetchSpy).not.toHaveBeenCalled()
  })

  it('shows validation errors from the API', async () => {
    const { fetchMock } = mockFetch([
      {
        method: 'POST',
        path: '/trips',
        status: 422,
        body: { detail: [{ loc: ['body'], msg: 'Value error, Start date cannot be in the past.' }] },
      },
    ])
    vi.stubGlobal('fetch', fetchMock)
    const { user } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Plan my trip' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Start date cannot be in the past.')
    expect(screen.getByRole('button', { name: 'Plan my trip' })).toBeEnabled()
  })
})
