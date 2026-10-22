import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, getTrip, parseErrorDetail } from './api'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('parseErrorDetail', () => {
  it('turns FastAPI validation errors into readable messages', () => {
    const messages = parseErrorDetail([
      { loc: ['body', 'travelers'], msg: 'Input should be greater than or equal to 1' },
      { loc: ['body'], msg: 'Value error, Origin and destination must be different.' },
    ])

    expect(messages).toEqual([
      'travelers: Input should be greater than or equal to 1',
      'trip: Origin and destination must be different.',
    ])
  })

  it('keeps plain string details', () => {
    expect(parseErrorDetail('Trip not found.')).toEqual(['Trip not found.'])
  })
})

describe('request errors', () => {
  it('throws an ApiError with the status code', async () => {
    vi.stubGlobal('fetch', async () => new Response(JSON.stringify({ detail: 'Trip not found.' }), { status: 404 }))

    await expect(getTrip('missing')).rejects.toMatchObject({ status: 404, messages: ['Trip not found.'] })
  })

  it('explains when the API cannot be reached', async () => {
    vi.stubGlobal('fetch', async () => {
      throw new TypeError('Failed to fetch')
    })

    const error = await getTrip('any').catch((caught: unknown) => caught)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).message).toMatch(/Cannot reach the API/)
  })
})
