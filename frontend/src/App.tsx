import { QueryClientProvider } from '@tanstack/react-query'
import { AppStateProvider } from '@/store/app-store'
import { HomePage } from '@/pages/home-page'
import { queryClient } from '@/services/query-client'

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppStateProvider>
        <HomePage />
      </AppStateProvider>
    </QueryClientProvider>
  )
}
