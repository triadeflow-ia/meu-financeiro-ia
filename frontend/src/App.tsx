import { Dashboard } from './Dashboard'

export type Cliente = {
  id: string
  nome: string
  documento_cpf_cnpj: string | null
  valor_mensalidade: number
  dia_vencimento: number
  status_ativo: boolean
  status_pagamento: 'pago' | 'pendente' | 'atrasado'
}

export type DashboardKPIs = {
  total_recebido: number
  notas_a_emitir: number
  clientes_inadimplentes: number
}

const API_BASE = '/api'

const API_KEY = import.meta.env.VITE_API_KEY as string | undefined

/** Headers comuns para todas as requisições à API (X-API-KEY quando configurado). */
function apiHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = { ...extra }
  if (API_KEY) headers['X-API-KEY'] = API_KEY
  return headers
}

export async function fetchClientes(): Promise<Cliente[]> {
  const r = await fetch(`${API_BASE}/clientes`, { headers: apiHeaders() })
  if (!r.ok) throw new Error('Erro ao carregar clientes')
  return r.json()
}

export async function fetchDashboardKPIs(): Promise<DashboardKPIs> {
  const r = await fetch(`${API_BASE}/clientes/dashboard`, { headers: apiHeaders() })
  if (!r.ok) throw new Error('Erro ao carregar KPIs')
  return r.json()
}

export async function bankSync(): Promise<{ message: string; transacoes_extrato: number; matches_criados: number }> {
  const r = await fetch(`${API_BASE}/bank/sync`, {
    method: 'POST',
    headers: apiHeaders(),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || 'Erro ao sincronizar Santander')
  }
  return r.json()
}

export async function exportContabilidade(): Promise<Blob> {
  const r = await fetch(`${API_BASE}/clientes/export/contabilidade`, { headers: apiHeaders() })
  if (!r.ok) throw new Error('Erro ao exportar')
  return r.blob()
}

export type ClientePayload = {
  nome: string
  documento_cpf_cnpj: string | null
  valor_mensalidade: number
  dia_vencimento: number
  status_ativo?: boolean
}

export async function createCliente(payload: ClientePayload): Promise<Cliente> {
  const r = await fetch(`${API_BASE}/clientes`, {
    method: 'POST',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || 'Erro ao criar cliente')
  }
  return r.json()
}

export async function updateCliente(id: string, payload: Partial<ClientePayload>): Promise<Cliente> {
  const r = await fetch(`${API_BASE}/clientes/${id}`, {
    method: 'PATCH',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || 'Erro ao atualizar cliente')
  }
  return r.json()
}

export async function deleteCliente(id: string): Promise<void> {
  const r = await fetch(`${API_BASE}/clientes/${id}`, {
    method: 'DELETE',
    headers: apiHeaders(),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || 'Erro ao excluir cliente')
  }
}

function App() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <Dashboard />
    </div>
  )
}

export default App
