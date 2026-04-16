import { axelorRequest } from '@/services/http/axelor-http'
import type { LoginPayload, SessionInfoResponse, UserSession } from '@/types/auth'


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

  if (!loginResponse.ok) {
    throw new Error('Login gagal, cek username/password atau sesi backend')
  }
  const responseData = (await loginResponse.json()) as SessionInfoResponse
  const accessToken = responseData.access_token
  const refreshToken = responseData.refresh_token

  if (!accessToken || !refreshToken) {
    throw new Error('Login Error')
  }

  return {
    accessToken,
    refreshToken,
    login: username,
    displayName: username,
  }
}

export async function logoutSession() {
  await axelorRequest('logout', { method: 'GET' })
}
