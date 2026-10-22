import { useEffect, useState } from 'react'

function prefersReducedMotion(): boolean {
  return typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function useCountUp(target: number, durationMs: number, delayMs: number): number {
  const [value, setValue] = useState(() => (prefersReducedMotion() ? target : 0))

  useEffect(() => {
    if (prefersReducedMotion()) {
      return
    }

    let frame = 0
    let start: number | null = null

    function step(time: number) {
      start ??= time
      const progress = Math.min((time - start) / durationMs, 1)
      const eased = 1 - (1 - progress) ** 3
      setValue(Math.round(target * eased))
      if (progress < 1) {
        frame = requestAnimationFrame(step)
      }
    }

    const timer = setTimeout(() => {
      frame = requestAnimationFrame(step)
    }, delayMs)

    return () => {
      clearTimeout(timer)
      cancelAnimationFrame(frame)
    }
  }, [target, durationMs, delayMs])

  return value
}
