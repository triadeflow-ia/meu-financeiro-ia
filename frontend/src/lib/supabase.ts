import { createClient, type SupabaseClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined

let client: SupabaseClient | null = null

/**
 * Cliente Supabase para uso no frontend (Realtime, etc.).
 * Retorna null se VITE_SUPABASE_URL ou VITE_SUPABASE_ANON_KEY não estiverem definidos.
 * Use a chave anon (pública), não a service_role.
 */
export function getSupabaseClient(): SupabaseClient | null {
  if (!url || !anonKey) return null
  if (!client) {
    client = createClient(url, anonKey)
  }
  return client
}
