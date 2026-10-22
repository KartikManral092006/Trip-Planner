interface Step {
  title: string
  detail: string
}

const STEPS: Step[] = [
  {
    title: 'You describe the trip',
    detail: 'Where from and to, dates, budget, who is going, and what you enjoy.',
  },
  {
    title: 'Agents research it',
    detail: 'Transport, stays, and things to do, each price with the page it came from.',
  },
  {
    title: 'Code does the maths',
    detail: 'Every price times nights and travelers, added up and compared with your budget.',
  },
  {
    title: 'The plan gets checked',
    detail: 'Dates, travel time, pace, and hotels are checked by code, then reviewed for fit.',
  },
  {
    title: 'You decide',
    detail: 'Approve it, or say what to change. Only the part you mention is researched again.',
  },
]

export function RouteSteps() {
  return (
    <ol className="lp-route">
      {STEPS.map((step, index) => (
        <li key={step.title} className="lp-station">
          <span className="lp-station-dot" aria-hidden="true">{index + 1}</span>
          <h3>{step.title}</h3>
          <p>{step.detail}</p>
        </li>
      ))}
    </ol>
  )
}
