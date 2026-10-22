import { formatMoney } from '../format'
import type { BudgetSummary } from '../types'

interface BudgetTableProps {
  budget: BudgetSummary
  currency: string
}

export function BudgetTable({ budget, currency }: BudgetTableProps) {
  const categories = Object.entries(budget.by_category).filter(([, amount]) => amount > 0)

  return (
    <section className="card budget" aria-labelledby="budget-title">
      <h2 id="budget-title">Budget</h2>

      <dl className="stats">
        <div>
          <dt>Total</dt>
          <dd>{formatMoney(budget.total, currency)}</dd>
        </div>
        <div>
          <dt>Budget</dt>
          <dd>{formatMoney(budget.budget, currency)}</dd>
        </div>
        <div className={budget.over_budget ? 'over' : 'under'}>
          <dt>{budget.over_budget ? 'Over by' : 'Remaining'}</dt>
          <dd>{formatMoney(Math.abs(budget.remaining), currency)}</dd>
        </div>
      </dl>

      <ul className="categories">
        {categories.map(([category, amount]) => (
          <li key={category}>
            <span>{category}</span>
            <span>{formatMoney(amount, currency)}</span>
          </li>
        ))}
      </ul>

      {budget.missing_categories.length > 0 && (
        <p className="notice warning">
          Not included (research missing): {budget.missing_categories.join(', ')}
        </p>
      )}

      <details>
        <summary>
          {budget.items.length} items · {budget.estimate_count} prices are estimates
        </summary>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Item</th>
                <th scope="col">Category</th>
                <th scope="col" className="number">Total</th>
                <th scope="col">Price</th>
              </tr>
            </thead>
            <tbody>
              {budget.items.map((item, index) => (
                <tr key={`${item.category}-${index}-${item.name}`}>
                  <td>
                    {item.source_url ? (
                      <a href={item.source_url} target="_blank" rel="noopener noreferrer">{item.name}</a>
                    ) : (
                      item.name
                    )}
                  </td>
                  <td>{item.category}</td>
                  <td className="number">{formatMoney(item.total, currency)}</td>
                  <td>
                    <span className={item.is_estimate ? 'tag estimate' : 'tag sourced'}>
                      {item.is_estimate ? 'estimate' : 'sourced'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  )
}
