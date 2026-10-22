import { useState, type ChangeEvent, type KeyboardEvent } from 'react'
import { Plus, X } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const SUGGESTIONS = [
  'food', 'history', 'museums', 'beaches', 'nature', 'nightlife',
  'shopping', 'temples', 'hiking', 'architecture', 'photography', 'cafes',
]
const MAX_INTERESTS = 10
const VISIBLE_SUGGESTIONS = 6

interface InterestsInputProps {
  id: string
  value: string[]
  onChange: (value: string[]) => void
}

export function InterestsInput({ id, value, onChange }: InterestsInputProps) {
  const [draft, setDraft] = useState('')
  const full = value.length >= MAX_INTERESTS
  const suggestions = SUGGESTIONS.filter((item) => !value.includes(item)).slice(0, VISIBLE_SUGGESTIONS)

  function add(raw: string) {
    const interest = raw.trim().toLowerCase()
    if (interest && !value.includes(interest) && !full) {
      onChange([...value, interest])
    }
    setDraft('')
  }

  function remove(interest: string) {
    onChange(value.filter((item) => item !== interest))
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      add(draft)
    } else if (event.key === 'Backspace' && draft === '' && value.length > 0) {
      remove(value[value.length - 1])
    }
  }

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    setDraft(event.target.value)
  }

  function handleBlur() {
    if (draft.trim()) {
      add(draft)
    }
  }

  return (
    <div className="grid gap-3">
      <div className="flex min-h-11 flex-wrap items-center gap-1.5 rounded-lg border border-input bg-background px-2 py-1.5 focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/30">
        {value.map((interest) => (
          <Badge key={interest} variant="secondary" className="h-7 gap-1 pr-1 pl-2.5 text-sm">
            {interest}
            <button
              type="button"
              data-slot="interest-remove"
              aria-label={`Remove ${interest}`}
              onClick={() => remove(interest)}
              className="rounded-full p-0.5 hover:bg-foreground/10 focus-visible:outline-2 focus-visible:outline-ring"
            >
              <X className="size-3.5" />
            </button>
          </Badge>
        ))}
        <input
          id={id}
          data-slot="interest-input"
          aria-label="Add an interest"
          value={draft}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          disabled={full}
          placeholder={full ? 'That is the maximum of 10' : value.length ? 'Add another' : 'Type an interest and press Enter'}
          className="h-7 min-w-36 flex-1 bg-transparent px-1 text-base outline-none placeholder:text-muted-foreground"
        />
      </div>
      {suggestions.length > 0 && !full && (
        <div className="flex flex-wrap gap-1.5" aria-label="Suggested interests">
          {suggestions.map((suggestion) => (
            <Button
              key={suggestion}
              type="button"
              variant="outline"
              size="sm"
              className="h-7 rounded-full"
              onClick={() => add(suggestion)}
            >
              <Plus />
              {suggestion}
            </Button>
          ))}
        </div>
      )}
    </div>
  )
}
