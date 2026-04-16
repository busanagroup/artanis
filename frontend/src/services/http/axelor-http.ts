import { clearStoredSession, readStoredAccessToken } from '@/services/auth/token-storage'

export type AxelorRequestInit = Omit<RequestInit, 'body'> & {
  body?: BodyInit | null
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
  const headers = new Headers(init.headers)

  headers.set('Accept', 'application/json')
  if (token) {
    headers.set('access_token', `Bearer ${token}`)
  }

  let body = init.body

  if (init.jsonBody !== undefined) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(init.jsonBody)
  }

  const response = await fetch(toAbsolutePath(path), {
    ...init,
    headers,
    body,
  })

  if (response.status === 401) {
    handleUnauthorized()
  }

  return response
}

export async function axelorJson<T>(path: string, init: AxelorRequestInit = {}) {
  const response = await axelorRequest(path, init)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} at ${path}`)
  }

  return (await response.json()) as T
}
