import { axelorJson, axelorRequest } from '@/services/http/axelor-http'
import type { LoginPayload, SessionInfoResponse, UserSession } from '@/types/auth'
import { useMutation, useQuery } from '@tanstack/react-query'


export async function loginWithPassword(payload: LoginPayload): Promise<UserSession> {
  const username = payload.username.trim()
  const password = payload.password.trim()

  if (!username || !password) {
    throw new Error('Username dan password wajib diisi')
  }

  const loginResponse = await axelorRequest('/auth/login', {
    method: 'POST',
    jsonBody: { username, password },
  })

  if (loginResponse.status < 200 || loginResponse.status >= 300) {
    throw new Error('Login gagal, cek username/password atau sesi backend')
  }
  const responseData = loginResponse.data as SessionInfoResponse
  const accessToken = responseData.access_token
  const refreshToken = responseData.refresh_token

  if (!accessToken || !refreshToken) {
    throw new Error('Login Error')
  }

  return {
    accessToken,
    refreshToken,
  }
}

export async function logoutSession() {
  await axelorRequest('logout', { method: 'GET' })
}

export async function callbackSession() {
  await axelorJson('/auth/callback', { method: 'GET' })
  return true
}

export function useSessionCallback(session: any) {
  return useQuery({
    queryKey: ['session-callback', session?.accessToken],
    queryFn: callbackSession,
    enabled: Boolean(session?.accessToken),
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  })
}