import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Landing } from './Landing'

describe('Landing', () => {
  it('explains the product and links to the planner', () => {
    render(<Landing hasTrip={false} />)

    expect(screen.getByRole('heading', { level: 1, name: 'A trip plan you can check.' })).toBeInTheDocument()
    const links = screen.getAllByRole('link', { name: 'Plan a trip' })
    expect(links.length).toBeGreaterThan(0)
    links.forEach((link) => expect(link).toHaveAttribute('href', '#/plan'))
  })

  it('shows the example plan with totals calculated from its lines', () => {
    render(<Landing hasTrip={false} />)

    expect(screen.getByRole('article', { name: 'Example plan from India to the UK' })).toBeInTheDocument()
    expect(screen.getByText('Over by ₹15,000')).toBeInTheDocument()
    expect(screen.getByLabelText('₹2,55,000')).toBeInTheDocument()
  })

  it('offers to return to a trip in progress', () => {
    render(<Landing hasTrip />)

    expect(screen.getAllByRole('link', { name: 'Back to your trip' }).length).toBeGreaterThan(0)
  })

  it('lists the planning steps in order', () => {
    render(<Landing hasTrip={false} />)

    const steps = screen.getAllByRole('heading', { level: 3 }).slice(0, 5).map((heading) => heading.textContent)
    expect(steps).toEqual([
      'You describe the trip',
      'Agents research it',
      'Code does the maths',
      'The plan gets checked',
      'You decide',
    ])
  })
})
