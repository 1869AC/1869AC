import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {createClient} from '@supabase/supabase-js'
export const supabase = createClient(import.meta.env.VITE_SUPABASE_URL || 'https://dummy.supabase.co', import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || 'dummy-key')
//PAGES!!
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)