import { useState, type ChangeEvent, type FormEvent, type ReactNode } from 'react'
import { addDays, startOfToday } from 'date-fns'
import {
  ArrowLeftRight,
  BedDouble,
  Bus,
  Car,
  Hotel,
  House,
  Minus,
  Plane,
  Plus,
  Shuffle,
  TrainFront,
  type LucideIcon,
} from 'lucide-react'
import type { DateRange } from 'react-day-picker'

import { ApiError, createTrip } from '@/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { localIsoDate } from '@/format'
import type { AccommodationType, FoodPreference, Pace, TransportMode, TripRequest } from '@/types'

import { DateRangeField } from './trip-form/DateRangeField'
import { InterestsInput } from './trip-form/InterestsInput'
import { MAX_TRIP_DAYS, tripDays } from './trip-form/tripMaths'
import { TripTicket } from './trip-form/TripTicket'

const MAX_TRAVELERS = 20
const CURRENCIES = ['INR', 'GBP', 'USD', 'EUR']

const PACES: { value: Pace; label: string; detail: string }[] = [
  { value: 'relaxed', label: 'Relaxed', detail: 'Up to 2 activities a day' },
  { value: 'moderate', label: 'Moderate', detail: 'Up to 3 activities a day' },
  { value: 'packed', label: 'Packed', detail: 'Up to 5 activities a day' },
]

const STAYS: { value: AccommodationType; label: string; icon: LucideIcon }[] = [
  { value: 'hotel', label: 'Hotel', icon: Hotel },
  { value: 'hostel', label: 'Hostel', icon: BedDouble },
  { value: 'homestay', label: 'Homestay', icon: House },
  { value: 'any', label: 'Any', icon: Shuffle },
]

const TRANSPORT: { value: TransportMode; label: string; icon: LucideIcon }[] = [
  { value: 'flight', label: 'Flight', icon: Plane },
  { value: 'train', label: 'Train', icon: TrainFront },
  { value: 'bus', label: 'Bus', icon: Bus },
  { value: 'car', label: 'Car', icon: Car },
]

const FOODS: { value: FoodPreference; label: string }[] = [
  { value: 'no preference', label: 'No preference' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'non-vegetarian', label: 'Non-vegetarian' },
  { value: 'vegan', label: 'Vegan' },
]

interface FormValues {
  origin: string
  destination: string
  dates: DateRange | undefined
  budget: string
  currency: string
  travelers: number
  interests: string[]
  accommodation_type: AccommodationType
  transport_preference: TransportMode[]
  food_preference: FoodPreference
  pace: Pace
  special_requirements: string
}

function defaultValues(): FormValues {
  const today = startOfToday()
  return {
    origin: 'India',
    destination: 'UK',
    dates: { from: addDays(today, 30), to: addDays(today, 36) },
    budget: '240000',
    currency: 'INR',
    travelers: 2,
    interests: ['museums', 'history', 'food'],
    accommodation_type: 'hotel',
    transport_preference: ['flight'],
    food_preference: 'no preference',
    pace: 'moderate',
    special_requirements: '',
  }
}

function validate(values: FormValues): string[] {
  const problems: string[] = []
  const days = tripDays(values.dates)

  if (!values.origin.trim()) problems.push('Add where you are starting from.')
  if (!values.destination.trim()) problems.push('Add where you are going.')
  if (values.origin.trim() && values.origin.trim().toLowerCase() === values.destination.trim().toLowerCase()) {
    problems.push('Start and destination must be different places.')
  }
  if (!days) problems.push('Choose a start and end date.')
  if (days && days > MAX_TRIP_DAYS) problems.push(`Trips can be at most ${MAX_TRIP_DAYS} days. This one is ${days}.`)
  if (!(Number(values.budget) > 0)) problems.push('Enter a budget above zero.')
  if (values.interests.length === 0) problems.push('Add at least one interest.')
  return problems
}

function toTripRequest(values: FormValues): TripRequest {
  return {
    origin: values.origin.trim(),
    destination: values.destination.trim(),
    start_date: localIsoDate(values.dates!.from!),
    end_date: localIsoDate(values.dates!.to!),
    budget: Number(values.budget),
    travelers: values.travelers,
    interests: values.interests,
    currency: values.currency,
    accommodation_type: values.accommodation_type,
    transport_preference: values.transport_preference,
    food_preference: values.food_preference,
    pace: values.pace,
    special_requirements: values.special_requirements.trim(),
  }
}

interface SectionProps {
  title: string
  hint?: string
  children: ReactNode
}

function Section({ title, hint, children }: SectionProps) {
  return (
    <section className="grid gap-4">
      <div>
        <h2 className="m-0 font-heading text-xl font-semibold">{title}</h2>
        {hint && <p className="text-sm text-muted-foreground">{hint}</p>}
      </div>
      {children}
    </section>
  )
}

interface TripFormProps {
  onCreated: (threadId: string) => void
}

export function TripForm({ onCreated }: TripFormProps) {
  const [values, setValues] = useState<FormValues>(defaultValues)
  const [errors, setErrors] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  function update<K extends keyof FormValues>(key: K, value: FormValues[K]) {
    setValues((current) => ({ ...current, [key]: value }))
  }

  function handleText(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  function swapRoute() {
    setValues((current) => ({ ...current, origin: current.destination, destination: current.origin }))
  }

  function changeTravelers(change: number) {
    setValues((current) => ({
      ...current,
      travelers: Math.min(MAX_TRAVELERS, Math.max(1, current.travelers + change)),
    }))
  }

  function handlePace(value: string) {
    if (value) update('pace', value as Pace)
  }

  function handleStay(value: string) {
    if (value) update('accommodation_type', value as AccommodationType)
  }

  function handleTransport(value: string[]) {
    if (value.length > 0) update('transport_preference', value as TransportMode[])
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const problems = validate(values)
    setErrors(problems)
    if (problems.length > 0) {
      return
    }

    setSubmitting(true)
    try {
      const started = await createTrip(toTripRequest(values))
      onCreated(started.thread_id)
    } catch (caught) {
      setErrors(caught instanceof ApiError ? caught.messages : ['Could not start planning.'])
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="grid grid-cols-[minmax(0,1fr)] items-start gap-8 lg:grid-cols-[minmax(0,1fr)_360px]"
    >
      <div className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-8 rounded-2xl border bg-card p-5 sm:p-8">
        <Section title="Where are you going?">
          <div className="grid grid-cols-[minmax(0,1fr)] items-end gap-3 sm:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
            <div className="grid gap-2">
              <Label htmlFor="origin">From</Label>
              <Input id="origin" name="origin" value={values.origin} onChange={handleText} className="h-11 text-base" autoComplete="off" />
            </div>
            <Button
              type="button"
              variant="outline"
              size="icon-lg"
              className="size-11 justify-self-center rounded-full"
              onClick={swapRoute}
              aria-label="Swap start and destination"
            >
              <ArrowLeftRight className="rotate-90 sm:rotate-0" />
            </Button>
            <div className="grid gap-2">
              <Label htmlFor="destination">To</Label>
              <Input id="destination" name="destination" value={values.destination} onChange={handleText} className="h-11 text-base" autoComplete="off" />
            </div>
          </div>

          <div className="grid grid-cols-[minmax(0,1fr)] gap-4 sm:grid-cols-[minmax(0,1fr)_auto]">
            <div className="grid gap-2">
              <Label htmlFor="dates">Dates</Label>
              <DateRangeField id="dates" value={values.dates} onChange={(dates) => update('dates', dates)} />
            </div>
            <div className="grid gap-2">
              <Label id="travelers-label">Travelers</Label>
              <div className="flex h-11 items-center gap-1 rounded-lg border border-input bg-background px-1" role="group" aria-labelledby="travelers-label">
                <Button type="button" variant="ghost" size="icon" onClick={() => changeTravelers(-1)} disabled={values.travelers <= 1} aria-label="Remove a traveler">
                  <Minus />
                </Button>
                <span className="w-8 text-center text-base font-semibold tabular-nums" aria-live="polite">{values.travelers}</span>
                <Button type="button" variant="ghost" size="icon" onClick={() => changeTravelers(1)} disabled={values.travelers >= MAX_TRAVELERS} aria-label="Add a traveler">
                  <Plus />
                </Button>
              </div>
            </div>
          </div>
        </Section>

        <Separator />

        <Section title="Budget" hint="The total for everyone, including travel and stays.">
          <div className="grid gap-3 sm:grid-cols-[1fr_120px]">
            <div className="grid gap-2">
              <Label htmlFor="budget">Total budget</Label>
              <Input id="budget" name="budget" type="number" inputMode="numeric" min="1" step="any" value={values.budget} onChange={handleText} className="h-11 text-base tabular-nums" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="currency">Currency</Label>
              <Select value={values.currency} onValueChange={(currency) => update('currency', currency)}>
                <SelectTrigger id="currency" className="h-11! w-full text-base">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CURRENCIES.map((currency) => (
                    <SelectItem key={currency} value={currency}>{currency}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </Section>

        <Separator />

        <Section title="How do you like to travel?">
          <div className="grid gap-2">
            <Label id="pace-label">Pace</Label>
            <ToggleGroup type="single" variant="outline" spacing={2} value={values.pace} onValueChange={handlePace} aria-labelledby="pace-label" className="grid w-full grid-cols-1 sm:grid-cols-3">
              {PACES.map((pace) => (
                <ToggleGroupItem key={pace.value} value={pace.value} aria-label={pace.label} className="h-auto flex-col items-start gap-0.5 px-4 py-3 text-left data-[state=on]:border-primary data-[state=on]:bg-accent data-[state=on]:text-accent-foreground">
                  <span className="text-base font-semibold">{pace.label}</span>
                  <span className="text-xs font-normal text-muted-foreground">{pace.detail}</span>
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          <div className="grid gap-2">
            <Label id="stay-label">Stay</Label>
            <ToggleGroup type="single" variant="outline" spacing={2} value={values.accommodation_type} onValueChange={handleStay} aria-labelledby="stay-label" className="flex-wrap">
              {STAYS.map(({ value, label, icon: Icon }) => (
                <ToggleGroupItem key={value} value={value} className="h-10 gap-2 px-4 data-[state=on]:border-primary data-[state=on]:bg-accent data-[state=on]:text-accent-foreground">
                  <Icon />
                  {label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          <div className="grid gap-2">
            <Label id="transport-label">Transport</Label>
            <ToggleGroup type="multiple" variant="outline" spacing={2} value={values.transport_preference} onValueChange={handleTransport} aria-labelledby="transport-label" className="flex-wrap">
              {TRANSPORT.map(({ value, label, icon: Icon }) => (
                <ToggleGroupItem key={value} value={value} className="h-10 gap-2 px-4 data-[state=on]:border-primary data-[state=on]:bg-accent data-[state=on]:text-accent-foreground">
                  <Icon />
                  {label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          <div className="grid gap-2 sm:max-w-64">
            <Label htmlFor="food">Food</Label>
            <Select value={values.food_preference} onValueChange={(food) => update('food_preference', food as FoodPreference)}>
              <SelectTrigger id="food" className="h-11! w-full text-base">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FOODS.map((food) => (
                  <SelectItem key={food.value} value={food.value}>{food.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </Section>

        <Separator />

        <Section title="What do you enjoy?" hint="The activity search uses these.">
          <InterestsInput id="interests" value={values.interests} onChange={(interests) => update('interests', interests)} />
          <div className="grid gap-2">
            <Label htmlFor="special_requirements">Anything else we should know?</Label>
            <Textarea
              id="special_requirements"
              name="special_requirements"
              rows={2}
              value={values.special_requirements}
              onChange={handleText}
              maxLength={500}
              placeholder="e.g. travelling with elderly parents, need step-free access"
              className="text-base"
            />
          </div>
        </Section>

      </div>

      <TripTicket
        origin={values.origin}
        destination={values.destination}
        dates={values.dates}
        travelers={values.travelers}
        budget={Number(values.budget)}
        currency={values.currency}
        pace={values.pace}
        interests={values.interests}
        errors={errors}
        submitting={submitting}
      />
    </form>
  )
}
