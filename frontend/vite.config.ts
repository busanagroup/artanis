import { defineConfig, loadEnv } from 'vite'
import { devtools } from '@tanstack/devtools-vite'
import tsconfigPaths from 'vite-tsconfig-paths'
import path from 'node:path'

import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const config = defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_PROXY_TARGET
  const proxyContext = env.VITE_PROXY_CONTEXT || '/'
  const buildBase = env.VITE_BUILD_BASE || '/'
  const targetBase = proxyTarget?.replace(/\/$/, '')
  const contextBase = proxyContext === '/' ? '' : proxyContext.replace(/\/$/, '')
  const buildOutputPath = path.resolve(__dirname, '..', 'src', 'artanis', 'asgi', 'templates', 'frontend')

  const rewriteToTargetContext = (path: string) => `${contextBase}${path}`
  const proxyRoutes = targetBase
    ? {
      '/ws': {
        target: targetBase,
        changeOrigin: true,
        rewrite: rewriteToTargetContext,
      },
      '/callback': {
        target: targetBase,
        changeOrigin: true,
        rewrite: rewriteToTargetContext,
      },
      '/login': {
        target: targetBase,
        changeOrigin: true,
        rewrite: rewriteToTargetContext,
      },
      '/logout': {
        target: targetBase,
        changeOrigin: true,
        rewrite: rewriteToTargetContext,
      },
    }
    : undefined

  return {
    base: buildBase,
    plugins: [
      devtools(),
      tsconfigPaths({ projects: ['./tsconfig.json'] }),
      tailwindcss(),
      viteReact(),
    ],
    build: {
      outDir: buildOutputPath,
      assetsDir: 'assets',
      emptyOutDir: true,
    },
    server: {
      proxy: proxyRoutes,
    },
  }
})

export default config
