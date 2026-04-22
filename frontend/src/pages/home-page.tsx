import { useQuery } from '@tanstack/react-query'
import { Spin } from 'antd'
import { LoginForm } from '@/modules/auth/components/login-form'
import { WorkspaceLayout } from '@/modules/workspace/workspace-layout'
import { useAppState } from '@/store/app-store'
import { useSessionCallback } from '@/services/api/auth/auth-api'

export function HomePage() {
  const { session } = useAppState()

  const { isPending } = useSessionCallback(session)

  if (session && isPending) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-3 text-center">
          <Spin size="large" />
          <p className="text-sm text-[#64739a]">Checking session...</p>
        </div>
      </main>
    )
  }

  if (!session) {
    return <LoginForm />
  }

  return <WorkspaceLayout />
}
