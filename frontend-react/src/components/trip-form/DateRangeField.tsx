import { format, startOfToday } from 'date-fns'
import { CalendarDays } from 'lucide-react'
import type { DateRange } from 'react-day-picker'

import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useMediaQuery } from '@/hooks/useMediaQuery'

import { describeLength, tripDays } from './tripMaths'

interface DateRangeFieldProps {
  id: string
  value: DateRange | undefined
  onChange: (value: DateRange | undefined) => void
}

function label(value: DateRange | undefined): string {
  if (!value?.from) {
    return 'Choose dates'
  }
  if (!value.to) {
    return `${format(value.from, 'd MMM yyyy')} to …`
  }
  return `${format(value.from, 'd MMM')} to ${format(value.to, 'd MMM yyyy')}`
}

export function DateRangeField({ id, value, onChange }: DateRangeFieldProps) {
  const wide = useMediaQuery('(min-width: 640px)')

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          className="h-11 w-full justify-start gap-2 px-3 text-base font-normal"
        >
          <CalendarDays className="text-muted-foreground" />
          <span className="min-w-0 truncate">{label(value)}</span>
          <span className="ml-auto hidden text-sm text-muted-foreground sm:inline">{describeLength(tripDays(value))}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="range"
          resetOnSelect
          numberOfMonths={wide ? 2 : 1}
          defaultMonth={value?.from}
          selected={value}
          onSelect={onChange}
          disabled={{ before: startOfToday() }}
          className="[--cell-size:--spacing(9)]"
        />
      </PopoverContent>
    </Popover>
  )
}
