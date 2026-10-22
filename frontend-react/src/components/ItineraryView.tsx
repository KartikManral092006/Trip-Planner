import { formatDate } from '../format'
import type { Itinerary } from '../types'

interface ItineraryViewProps {
  itinerary: Itinerary
}

export function ItineraryView({ itinerary }: ItineraryViewProps) {
  return (
    <section className="itinerary" aria-labelledby="itinerary-title">
      <h2 id="itinerary-title">{itinerary.title}</h2>

      {itinerary.warnings.length > 0 && (
        <div className="notice warning">
          <h3>Warnings</h3>
          <ul>
            {itinerary.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      )}

      <ol className="days">
        {itinerary.days.map((day) => (
          <li key={day.date} className="card day">
            <header>
              <span className="day-number">Day {day.day}</span>
              <time dateTime={day.date}>{formatDate(day.date)}</time>
              {day.is_travel_day && <span className="badge">Travel day</span>}
            </header>
            <p className="location">{day.location}</p>
            {day.activities.length > 0 && (
              <ul className="activities">
                {day.activities.map((activity, index) => (
                  <li key={`${day.date}-${index}-${activity}`}>{activity}</li>
                ))}
              </ul>
            )}
            {day.stay && <p className="stay"><strong>Stay:</strong> {day.stay}</p>}
          </li>
        ))}
      </ol>

      {itinerary.suggestions.length > 0 && (
        <div className="notice info">
          <h3>Suggestions</h3>
          <ul>
            {itinerary.suggestions.map((suggestion) => <li key={suggestion}>{suggestion}</li>)}
          </ul>
        </div>
      )}
    </section>
  )
}
