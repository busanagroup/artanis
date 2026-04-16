import type { UserSession } from '@/types/auth'

const ACCESS_TOKEN_COOKIE = 'access_token'
const REFRESH_TOKEN_COOKIE = 'refresh_token'
const LOGIN_COOKIE = 'login'

function canUseCookies() {
  return typeof document !== 'undefined'
}

function readCookie(name: string) {
  if (!canUseCookies()) {
    return null
  }

  const match = document.cookie.match(new RegExp(`(^|;\\s*)(${name})=([^;]*)`))
  return match ? decodeURIComponent(match[3]) : null
}

function writeCookie(name: string, value: string, maxAgeSeconds = 60 * 60 * 24) {
  if (!canUseCookies()) {
    return
  }

  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; SameSite=Lax`
}

function clearCookie(name: string) {
  if (!canUseCookies()) {
    return
  }

  document.cookie = `${name}=; path=/; max-age=0; SameSite=Lax`
}

export function readStoredSession(): UserSession | null {
  const accessToken = readCookie(ACCESS_TOKEN_COOKIE)
  const refreshToken = readCookie(REFRESH_TOKEN_COOKIE)

  if (!accessToken || !refreshToken) {
    return null
  }

  return {
    accessToken,
    refreshToken,
    login: readCookie(LOGIN_COOKIE) ?? undefined,
  }
}

export function writeStoredSession(session: UserSession) {
  writeCookie(ACCESS_TOKEN_COOKIE, session.accessToken)
  writeCookie(REFRESH_TOKEN_COOKIE, session.refreshToken)
  if (session.login) writeCookie(LOGIN_COOKIE, session.login)
}

export function clearStoredSession() {
  clearCookie(ACCESS_TOKEN_COOKIE)
  clearCookie(REFRESH_TOKEN_COOKIE)
  clearCookie(LOGIN_COOKIE)
}

export function readStoredAccessToken() {
  return readCookie(ACCESS_TOKEN_COOKIE)
}
