import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  onReset: () => void
}

interface ErrorBoundaryState {
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unexpected UI error', error, info.componentStack)
  }

  handleReset = () => {
    this.setState({ error: null })
    this.props.onReset()
  }

  render() {
    if (this.state.error) {
      return (
        <section className="card notice error" role="alert">
          <h2>Something went wrong on this page.</h2>
          <p>{this.state.error.message}</p>
          <button type="button" onClick={this.handleReset}>Start over</button>
        </section>
      )
    }
    return this.props.children
  }
}
