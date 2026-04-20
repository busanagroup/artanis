import axios, { type AxiosRequestConfig, type AxiosResponse, isAxiosError } from 'axios'
import { clearStoredSession, readStoredAccessToken } from '@/services/auth/token-storage'

export const API_TIMEOUT_MS = 60_000

export type AxelorRequestInit = Omit<AxiosRequestConfig, 'url' | 'data'> & {
  jsonBody?: unknown
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
