import { showPush } from "@/utils/alert"

const getErrorMessage = (err: unknown): string => {
  if (typeof err === 'string') return err
  if (err instanceof Error) return err.message
  try {
    return JSON.stringify(err)
  } catch {
    return 'Unknown error'
  }
}

export const handleError = (err: unknown, type: string) => {
  const errorMessage = getErrorMessage(err)
  console.error(`[${type}]`, err)
  showPush('app.error', { error: errorMessage }, 'alert-warning', 'ri-error-warning-line')
  if (type === 'Unhandled Promise Rejection') {
    console.error('Unhandled Promise Rejection:', err)
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  }
}