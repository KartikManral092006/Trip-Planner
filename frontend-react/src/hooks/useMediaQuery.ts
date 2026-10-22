import { useEffect, useState } from 'react'

function matches(query: string): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia(query).matches
}

export function useMediaQuery(query: string): boolean {
  const [isMatch, setIsMatch] = useState(() => matches(query))

  useEffect(() => {
    if (typeof window.matchMedia !== 'function') {
      return
    }
    const list = window.matchMedia(query)
    function handleChange() {
      setIsMatch(list.matches)
    }
    handleChange()
    list.addEventListener('change', handleChange)
    return () => list.removeEventListener('change', handleChange)
  }, [query])

  return isMatch
}
