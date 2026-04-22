import axios, { type AxiosRequestConfig, type AxiosResponse, isAxiosError } from 'axios'
import {
  clearStoredSession,
  readStoredAccessToken,
  readStoredRefreshToken,
  writeStoredSession,
} from '@/services/auth/token-storage'
import type { SessionInfoResponse } from '@/types/auth'

export const API_TIMEOUT_MS = 60_000

export type AxelorRequestInit = Omit<AxiosRequestConfig, 'url' | 'data'> & {
  jsonBody?: unknown
  _retry?: Boolean
}

function toAbsolutePath(path: string) {
  if (path.startsWith('/')) {
    return path
  }
  return `/${path}`
}

function handleUnauthorized() {
  clearStoredSession()
  window.location.reload()
}

export async function refreshSession() {
  const refreshToken = readStoredRefreshToken()

  if (!refreshToken) {
    return false
  }

  const response = await axios({
    method: 'POST',
    url: '/auth/refresh',
    data: { refresh_token: refreshToken },
    timeout: API_TIMEOUT_MS,
    validateStatus: () => true,
  })

  if (response.status < 200 || response.status >= 300) {
    return false
  }

  writeStoredSession({
    accessToken: response.data.access_token,
    refreshToken: response.data.refresh_token,
  })

  return true
}


export async function axelorRequest(path: string, init: AxelorRequestInit = {}) {
  const token = readStoredAccessToken()
  const headers = {
    ...(init.headers as Record<string, string> | undefined),
    Accept: 'application/json',
    ...(token ? { access_token: `Bearer ${token}` } : {}),
    ...(init.jsonBody !== undefined ? { 'Content-Type': 'application/json' } : {}),
  }

  try {
    const response = await axios({
      ...init,
      url: toAbsolutePath(path),
      headers,
      data: init.jsonBody,
      timeout: init.timeout ?? API_TIMEOUT_MS,
      validateStatus: () => true,
    })

    if (response.status === 401) {
      const canRefresh =
        !init._retry &&
        path !== '/auth/login' &&
        path !== '/auth/refresh'

      if (canRefresh) {
        const refreshed = await refreshSession()

        if (refreshed) {
          return axelorRequest(path, { ...init, _retry: true })
        }
      }
      handleUnauthorized()
    }

    return response
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 401) {
      handleUnauthorized()
    }
    throw error
  }
}

export async function axelorJson<T>(path: string, init: AxelorRequestInit = {}) {
  const response = await axelorRequest(path, init) as AxiosResponse<T>

  if (response.status < 200 || response.status >= 300) {
    throw new Error(`HTTP ${response.status} at ${path}`)
  }

  return response.data
}
