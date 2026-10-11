from supabase import create_client
VITE_SUPABASE_URL = "https://qzqhzwsfubazirdzxnse.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_9mpzUg4eXNLneiT-3O65VA_IhjFNt8E"
supabase = create_client(VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY)