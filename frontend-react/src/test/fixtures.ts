import type { Trip } from '../types'

export function makeTrip(changes: Partial<Trip> = {}): Trip {
  return {
    thread_id: 'trip-1',
    status: 'waiting_for_approval',
    error: null,
    next_steps: [],
    trip: {
      origin: 'Dehradun',
      destination: 'Goa',
      start_date: '2026-12-10',
      end_date: '2026-12-11',
      travelers: 2,
      currency: 'INR',
    },
    itinerary: {
      title: 'Goa Getaway',
      days: [
        { day: 1, date: '2026-12-10', location: 'Goa', is_travel_day: true, activities: ['Fly to Goa'], stay: 'Sunrise Inn' },
        { day: 2, date: '2026-12-11', location: 'Goa', is_travel_day: false, activities: ['Baga Beach'], stay: null },
      ],
      warnings: ['The plan is over budget by ₹4,460.'],
      suggestions: ['Choose a cheaper hotel.'],
    },
    itinerary_markdown: '# Goa Getaway',
    budget_summary: {
      items: [
        {
          name: 'Flight Dehradun to Goa',
          category: 'transport',
          amount: 9000,
          quantity: 1,
          per_person: true,
          source_url: 'https://example.com/flight',
          is_estimate: true,
          total: 18000,
        },
      ],
      by_category: { transport: 18000, accommodation: 0, activities: 0, food: 0, other: 0 },
      total: 34460,
      budget: 30000,
      remaining: -4460,
      over_budget: true,
      estimate_count: 1,
      missing_categories: [],
    },
    rule_issues: [],
    evaluation_feedback: '',
    revisions: 1,
    feedback_rounds: 0,
    ...changes,
  }
}

interface MockRoute {
  method: string
  path: string
  status?: number
  body: unknown
}

export function mockFetch(routes: MockRoute[]) {
  const calls: { method: string; path: string; body: unknown }[] = []

  const fetchMock = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input))
    const method = init?.method ?? 'GET'
    calls.push({ method, path: url.pathname, body: init?.body ? JSON.parse(String(init.body)) : null })

    const index = routes.findIndex((route) => route.method === method && route.path === url.pathname)
    if (index === -1) {
      throw new Error(`Unexpected request ${method} ${url.pathname}`)
    }
    const [route] = routes.splice(index, 1)
    return new Response(JSON.stringify(route.body), { status: route.status ?? 200 })
  }

  return { fetchMock, calls }
}
