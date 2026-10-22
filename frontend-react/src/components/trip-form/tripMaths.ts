import { differenceInCalendarDays } from 'date-fns'
import type { DateRange } from 'react-day-picker'

export const MAX_TRIP_DAYS = 14

export function tripDays(dates: DateRange | undefined): number | null {
  if (!dates?.from || !dates.to) {
    return null
  }
  return differenceInCalendarDays(dates.to, dates.from) + 1
}

export function perPersonPerDay(budget: number, travelers: number, days: number | null): number | null {
  if (!days || !travelers || !(budget > 0)) {
    return null
  }
  return budget / travelers / days
}

export function describeLength(days: number | null): string {
  if (!days) {
    return 'Pick your dates'
  }
  const nights = days - 1
  return `${days} ${days === 1 ? 'day' : 'days'}, ${nights} ${nights === 1 ? 'night' : 'nights'}`
}
