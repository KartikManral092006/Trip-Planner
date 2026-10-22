import './landing.css'

import { PLAN_HREF } from '../../hooks/useHashRoute'
import { PlanTicket } from './PlanTicket'
import { RouteSteps } from './RouteSteps'

interface LandingProps {
  hasTrip: boolean
}

export function Landing({ hasTrip }: LandingProps) {
  const ctaLabel = hasTrip ? 'Back to your trip' : 'Plan a trip'

  return (
    <div className="lp">
      <header className="lp-nav">
        <a className="lp-wordmark" href="#/">AI Travel Planner</a>
        <a className="lp-button lp-button-small" href={PLAN_HREF}>{ctaLabel}</a>
      </header>

      <main>
        <section className="lp-hero" aria-labelledby="lp-title">
          <div className="lp-hero-copy">
            <h1 id="lp-title">A trip plan you can check.</h1>
            <p className="lp-lede">
              Tell it where, when, and how much. Agents research trains, flights, stays,
              and things to do. Code adds up every rupee. Nothing is final until you approve it.
            </p>
            <div className="lp-actions">
              <a className="lp-button" href={PLAN_HREF}>{ctaLabel}</a>
              <a className="lp-link" href="#how">See how a plan is made</a>
            </div>
          </div>
          <PlanTicket />
        </section>

        <section id="how" className="lp-section" aria-labelledby="lp-how">
          <h2 id="lp-how">How a plan is made</h2>
          <RouteSteps />
        </section>

        <section className="lp-section" aria-labelledby="lp-proof">
          <h2 id="lp-proof">Built to be checked</h2>
          <div className="lp-proof">
            <div className="lp-proof-row">
              <div>
                <h3>The AI finds prices. Code adds them up.</h3>
                <p>
                  Language models are good at reading travel pages and bad at arithmetic,
                  so they only report the price, the units, and who pays. The totals are plain Python.
                </p>
              </div>
              <p className="lp-specimen lp-sum">
                <span>₹32,000 × 2 travelers × 2 flights</span>
                <strong>= ₹1,28,000</strong>
              </p>
            </div>

            <div className="lp-proof-row">
              <div>
                <h3>Every price shows where it came from</h3>
                <p>
                  Each line links to the page it was found on. When a price could not be
                  confirmed, the plan says it is an estimate instead of guessing quietly.
                </p>
              </div>
              <ul className="lp-specimen lp-tags" aria-label="Example price labels">
                <li><span className="lp-tag lp-tag-sourced">sourced</span> Delhi to London flight</li>
                <li><span className="lp-tag lp-tag-estimate">estimate</span> Heathrow to the hotel</li>
              </ul>
            </div>

            <div className="lp-proof-row">
              <div>
                <h3>Change one thing, keep the rest</h3>
                <p>
                  Ask for a cheaper hotel and only the hotel search runs again. Your train,
                  activities, and everything you already liked stay as they were.
                </p>
              </div>
              <p className="lp-specimen lp-quote">
                “Find a cheaper hotel near King's Cross”
                <span>Searching places to stay again</span>
              </p>
            </div>
          </div>
        </section>

        <section className="lp-section lp-notes" aria-labelledby="lp-notes">
          <h2 id="lp-notes">Good to know</h2>
          <ul>
            <li>A plan takes a few minutes, because the searches run one after another.</li>
            <li>Prices are estimates from the web. Check them before you book.</li>
            <li>Trips can be up to 14 days long.</li>
          </ul>
        </section>

        <section className="lp-closing" aria-labelledby="lp-closing">
          <h2 id="lp-closing">Where are you going next?</h2>
          <a className="lp-button" href={PLAN_HREF}>{ctaLabel}</a>
        </section>
      </main>

      <footer className="lp-footer">
        <p>Built with LangGraph, FastAPI, and React.</p>
      </footer>
    </div>
  )
}
