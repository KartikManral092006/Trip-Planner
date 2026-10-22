import { useEffect, useState } from 'react'

export type Route = 'home' | 'plan'

export const PLAN_HREF = '#/plan'
export const HOME_HREF = '#/'

function readRoute(): Route {
  return window.location.hash === PLAN_HREF ? 'plan' : 'home'
}

export function useHashRoute(): Route {
  const [route, setRoute] = useState<Route>(readRoute)

  useEffect(() => {
    function handleHashChange() {
      setRoute(readRoute())
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [route])

  return route
}
