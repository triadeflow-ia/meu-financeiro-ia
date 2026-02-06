import { useEffect } from 'react'

export type ToastType = 'success' | 'error'

type ToastProps = {
  message: string
  type: ToastType
  onDismiss: () => void
  duration?: number
}

export function Toast({ message, type, onDismiss, duration = 5000 }: ToastProps) {
  useEffect(() => {
    const t = setTimeout(onDismiss, duration)
    return () => clearTimeout(t)
  }, [onDismiss, duration])

  const isSuccess = type === 'success'
  return (
    <div
      role="alert"
      className="fixed bottom-6 right-6 z-50 flex max-w-sm items-center gap-3 rounded-lg border px-4 py-3 shadow-lg toast-enter"
      style={{
        background: isSuccess ? 'rgb(6 95 70 / 0.95)' : 'rgb(185 28 28 / 0.95)',
        borderColor: isSuccess ? 'rgb(16 185 129 / 0.5)' : 'rgb(248 113 113 / 0.5)',
        color: 'white',
      }}
    >
      {isSuccess ? (
        <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      )}
      <p className="text-sm font-medium">{message}</p>
    </div>
  )
}
