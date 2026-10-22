export type TripStatus =
  | 'running'
  | 'waiting_for_approval'
  | 'approved'
  | 'rejected'
  | 'failed'

export type Pace = 'relaxed' | 'moderate' | 'packed'
export type AccommodationType = 'any' | 'hotel' | 'hostel' | 'homestay'
export type FoodPreference = 'no preference' | 'vegetarian' | 'non-vegetarian' | 'vegan'
export type TransportMode = 'train' | 'flight' | 'bus' | 'car'

export interface TripRequest {
  origin: string
  destination: string
  start_date: string
  end_date: string
  budget: number
  travelers: number
  interests: string[]
  currency: string
  accommodation_type: AccommodationType
  transport_preference: TransportMode[]
  food_preference: FoodPreference
  pace: Pace
  special_requirements: string
}

export interface DayPlan {
  day: number
  date: string
  location: string
  is_travel_day: boolean
  activities: string[]
  stay: string | null
}

export interface Itinerary {
  title: string
  days: DayPlan[]
  warnings: string[]
  suggestions: string[]
}

export interface BudgetItem {
  name: string
  category: string
  amount: number
  quantity: number
  per_person: boolean
  source_url: string | null
  is_estimate: boolean
  duration_hours?: number | null
  total: number
}

export interface BudgetSummary {
  items: BudgetItem[]
  by_category: Record<string, number>
  total: number
  budget: number
  remaining: number
  over_budget: boolean
  estimate_count: number
  missing_categories: string[]
}

export interface TripInfo {
  origin: string
  destination: string
  start_date: string
  end_date: string
  travelers: number
  currency: string
}

export interface Trip {
  thread_id: string
  status: TripStatus
  error: string | null
  next_steps: string[]
  trip: TripInfo
  itinerary: Itinerary | null
  itinerary_markdown: string | null
  budget_summary: BudgetSummary | null
  rule_issues: string[]
  evaluation_feedback: string
  revisions: number
  feedback_rounds: number
}
