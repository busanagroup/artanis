import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Alert, Button, Form, Input, Typography } from 'antd'
import { EyeInvisibleOutlined, EyeTwoTone, LockOutlined, UserOutlined } from '@ant-design/icons'
import { loginWithPassword } from '@/services/api/auth/auth-api'
import { useAppActions } from '@/store/app-store'

const { Title, Text } = Typography

export function LoginForm() {
  const { loginSuccess } = useAppActions()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const loginMutation = useMutation({
    mutationFn: loginWithPassword,
    onSuccess: (session) => {
      setErrorMessage(null)
      loginSuccess(session)
    },
    onError: (error) => {
      setErrorMessage(error instanceof Error ? error.message : 'Login gagal')
    },
  })

  const handleSubmit = () => {
    loginMutation.mutate({ username, password })
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-white">
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.98)_0%,rgba(255,255,255,0.95)_46%,rgba(243,247,255,0.96)_100%)]" />

      <div className="relative grid min-h-screen grid-cols-1 lg:grid-cols-[minmax(420px,540px)_1fr]">
        <section className="flex items-center px-6 py-12 sm:px-10 lg:px-16 xl:px-24">
          <div className="w-full max-w-[448px]">
            <div className="mb-10">
              <Title level={1} className="!mb-2 !text-[44px] !font-semibold !tracking-[-0.03em] !text-[#16356b]">
                Sign In
              </Title>
              <Text className="!text-[15px] !leading-7 !text-[#64739a]">
                Enter your username and password to sign in!
              </Text>
            </div>

            <Form layout="vertical" requiredMark={false} onFinish={handleSubmit} className="space-y-1">
              <Form.Item
                label={<span className="text-sm font-semibold text-[#233d73]">Username <span className="text-red-500">*</span></span>}
                validateStatus={errorMessage ? 'error' : ''}
                className="!mb-6"
              >
                <Input
                  size="large"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="enter username"
                  prefix={<UserOutlined className="text-[#93a0c0]" />}
                  autoComplete="username"
                  className="!h-[50px] !rounded-xl !border-[#cfd8ea] !px-3 hover:!border-[#8da2d6] focus:!border-[#6a5cff]"
                />
              </Form.Item>

              <Form.Item
                label={<span className="text-sm font-semibold text-[#233d73]">Password <span className="text-red-500">*</span></span>}
                validateStatus={errorMessage ? 'error' : ''}
                help={errorMessage ? <span className="text-sm">{errorMessage}</span> : null}
                className="!mb-10"
              >
                <Input.Password
                  size="large"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  prefix={<LockOutlined className="text-[#93a0c0]" />}
                  autoComplete="current-password"
                  iconRender={(visible) => (visible ? <EyeTwoTone twoToneColor="#6676a5" /> : <EyeInvisibleOutlined className="text-[#6676a5]" />)}
                  className="!h-[50px] !rounded-xl !border-[#cfd8ea] !px-3 hover:!border-[#8da2d6] focus:!border-[#6a5cff]"
                />
              </Form.Item>

              {errorMessage ? (
                <Alert
                  type="error"
                  showIcon
                  message={errorMessage}
                  className="!mb-6 !rounded-xl !border-0 !bg-[#fff2f0]"
                />
              ) : null}

              <Button
                type="primary"
                htmlType="submit"
                loading={loginMutation.isPending}
                className="!h-[52px] !w-full !rounded-xl !border-0 !text-base !font-semibold !shadow-none"
                style={{
                  background: 'linear-gradient(90deg, #5b10ff 0%, #7d19ff 52%, #6113ff 100%)',
                }}
              >
                {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
              </Button>
            </Form>
          </div>
        </section>

        <section className="relative hidden overflow-hidden lg:flex lg:items-center lg:justify-center">
          <div
            className="absolute inset-0 opacity-80"
            style={{
              backgroundImage:
                'linear-gradient(to right, rgba(130,150,190,0.12) 1px, transparent 1px), linear-gradient(to bottom, rgba(130,150,190,0.12) 1px, transparent 1px)',
              backgroundSize: '52px 52px',
            }}
          />
          <div className="absolute left-[18%] top-[28%] h-24 w-24 rounded-2xl bg-white/40 blur-2xl" />
          <div className="absolute right-[14%] top-[58%] h-32 w-32 rounded-3xl bg-[#dfe8fb]/70 blur-2xl" />
          <div className="absolute left-[48%] top-[46%] h-40 w-40 rounded-full bg-[#edf3ff] blur-3xl" />

          <div className="relative w-full max-w-[520px] px-10">
            <div className="flex items-center gap-4">
              <div className="relative h-16 w-16 shrink-0">
                <div className="absolute left-2 top-1 h-14 w-4 rotate-[28deg] rounded-full bg-[#16356b]" />
                <div className="absolute left-8 top-0 h-16 w-2 rounded-full bg-[#ffcb05]" />
              </div>

              <div>
                <p className="text-[40px] font-semibold leading-none tracking-[-0.04em] text-[#1c4587]">ARTANIS</p>
                <p className="mt-2 text-sm tracking-[0.28em] text-[#7b8db5]">OPEN SUITE</p>
                <p className="mt-1 text-base text-[#8b9cc0]">Enterprise Workspace Platform</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
