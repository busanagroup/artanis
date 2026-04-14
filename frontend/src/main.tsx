import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'

import './styles.css'

const rootElement = document.getElementById('app')

if (!rootElement) {
  throw new Error('App root element not found')
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
