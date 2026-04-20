export type UserSession = {
  accessToken: string
  refreshToken: string
  login?: string
  username?: string
  first_name?: string
  last_name?: string
  email?: string
  cono?: string
  coname?: string
  dvno?: string
  dvname?: string
}

export type LoginPayload = {
  username: string
  password: string
}

export type SessionInfoResponse = {
  access_token?: string
  refresh_token?: string
  username?: string
  first_name?: string
  last_name?: string
  email?: string
  cono?: string
  coname?: string
  dvno?: string
  dvname?: string
}
