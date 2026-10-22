import { format } from 'date-fns'
import { LoaderCircle } from 'lucide-react'
import type { DateRange } from 'react-day-picker'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { formatMoney } from '@/format'

import { describeLength, perPersonPerDay, tripDays } from './tripMaths'

interface TripTicketProps {
  origin: string
  destination: string
  dates: DateRange | undefined
  travelers: number
  budget: number
  currency: string
  pace: string
  interests: string[]
  errors: string[]
  submitting: boolean
}

function dateLine(dates: DateRange | undefined): string {
  if (!dates?.from || !dates.to) {
    return 'Dates not chosen yet'
  }
  return `${format(dates.from, 'd MMM')} to ${format(dates.to, 'd MMM')}`
}

export function TripTicket(props: TripTicketProps) {
  const days = tripDays(props.dates)
  const daily = perPersonPerDay(props.budget, props.travelers, days)

  return (
    <aside
      aria-label="Trip summary"
      className="relative rounded-2xl bg-paper p-6 text-[#15233f] shadow-[0_18px_34px_-8px_rgba(21,35,63,0.28),0_2px_5px_rgba(21,35,63,0.12)] lg:sticky lg:top-6"
    >
      <p className="font-heading text-3xl leading-none font-bold [font-stretch:85%] break-words">
        {props.origin.trim() || 'From'} → {props.destination.trim() || 'To'}
      </p>

      <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <div>
          <dt className="text-[#5a6876]">Dates</dt>
          <dd className="font-semibold">{dateLine(props.dates)}</dd>
        </div>
        <div>
          <dt className="text-[#5a6876]">Length</dt>
          <dd className="font-semibold">{describeLength(days)}</dd>
        </div>
        <div>
          <dt className="text-[#5a6876]">Travelers</dt>
          <dd className="font-semibold tabular-nums">{props.travelers}</dd>
        </div>
        <div>
          <dt className="text-[#5a6876]">Pace</dt>
          <dd className="font-semibold capitalize">{props.pace}</dd>
        </div>
      </dl>

      {props.interests.length > 0 && (
        <p className="mt-4 text-sm text-[#3d4a57]">For {props.interests.join(', ')}</p>
      )}

      <div className="relative mt-6 border-t-2 border-dashed border-[#b9c4bc] pt-5">
        <span aria-hidden="true" className="absolute -top-[14px] -left-[38px] size-[26px] rounded-full bg-background" />
        <span aria-hidden="true" className="absolute -top-[14px] -right-[38px] size-[26px] rounded-full bg-background" />

        <div className="flex items-baseline justify-between gap-3">
          <span className="text-sm text-[#5a6876]">Budget</span>
          <span className="font-heading text-3xl font-bold tabular-nums">
            {props.budget > 0 ? formatMoney(props.budget, props.currency) : 'Not set'}
          </span>
        </div>
        <p className="mt-1 text-right text-sm text-[#3d4a57]" aria-live="polite">
          {daily
            ? `About ${formatMoney(daily, props.currency)} per person a day`
            : 'Add dates and a budget to see the daily amount'}
        </p>

        {props.errors.length > 0 && (
          <Alert variant="destructive" role="alert" className="mt-5 border-stamp/40 bg-white text-stamp">
            <AlertTitle>Check these before planning</AlertTitle>
            <AlertDescription className="text-stamp">
              <ul className="list-disc pl-4">
                {props.errors.map((message) => <li key={message}>{message}</li>)}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        <Button type="submit" size="lg" className="mt-6 h-12 w-full text-base" disabled={props.submitting}>
          {props.submitting && <LoaderCircle className="animate-spin" />}
          {props.submitting ? 'Starting…' : 'Plan my trip'}
        </Button>
        <p className="mt-3 text-center text-xs text-[#5a6876]">
          Research takes a few minutes. You approve the plan at the end.
        </p>
      </div>
    </aside>
  )
}
