export type UserSession = {
  accessToken: string
  refreshToken: string
  login?: string
  displayName?: string
}

export type LoginPayload = {
  username: string
  password: string
}

export type SessionInfoResponse = {
  access_token?: string
  refresh_token?: string
}
