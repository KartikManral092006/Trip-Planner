import type { CSSProperties } from 'react'

import { formatMoney } from '../../format'
import { useCountUp } from '../../hooks/useCountUp'

interface TicketLine {
  item: string
  maths: string
  total: number
}

const LINES: TicketLine[] = [
  { item: 'Flight Delhi to London', maths: '₹32,000 × 2 travelers', total: 64000 },
  { item: 'Flight home', maths: '₹32,000 × 2 travelers', total: 64000 },
  { item: 'Hotel in London', maths: '₹9,500 × 6 nights', total: 57000 },
  { item: 'Food', maths: '₹3,000 × 7 days × 2 travelers', total: 42000 },
  { item: 'UK visitor visas', maths: '₹14,000 × 2 travelers', total: 28000 },
]

const BUDGET = 240000
const TOTAL = LINES.reduce((sum, line) => sum + line.total, 0)
const LINE_DELAY_MS = 140
const TOTAL_DELAY_MS = 400 + LINES.length * LINE_DELAY_MS

export function PlanTicket() {
  const shownTotal = useCountUp(TOTAL, 900, TOTAL_DELAY_MS)

  return (
    <figure className="lp-ticket-wrap">
      <article className="lp-ticket" aria-label="Example plan from India to the UK">
        <header className="lp-ticket-head">
          <p className="lp-ticket-route">India → UK</p>
          <dl className="lp-ticket-meta">
            <div>
              <dt>Dates</dt>
              <dd>12 to 18 Jun</dd>
            </div>
            <div>
              <dt>Travelers</dt>
              <dd>2</dd>
            </div>
            <div>
              <dt>Budget</dt>
              <dd>{formatMoney(BUDGET, 'INR')}</dd>
            </div>
          </dl>
        </header>

        <ol className="lp-ticket-lines">
          {LINES.map((line, index) => (
            <li
              key={line.item}
              className="lp-ticket-line"
              style={{ '--line': index } as CSSProperties}
            >
              <span className="lp-line-item">{line.item}</span>
              <span className="lp-line-maths">{line.maths}</span>
              <span className="lp-line-total">{formatMoney(line.total, 'INR')}</span>
            </li>
          ))}
        </ol>

        <footer className="lp-ticket-foot">
          <p className="lp-ticket-total">
            <span>Total</span>
            <strong aria-label={formatMoney(TOTAL, 'INR')}>{formatMoney(shownTotal, 'INR')}</strong>
          </p>
          <p className="lp-stamp">Over by {formatMoney(TOTAL - BUDGET, 'INR')}</p>
          <p className="lp-ticket-tip">
            Cheaper option found: a hotel outside central London saves about ₹18,000.
          </p>
        </footer>
      </article>
      <figcaption>Example plan. Prices are illustrative estimates.</figcaption>
    </figure>
  )
}
