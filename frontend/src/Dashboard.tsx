import { useState, useEffect, useCallback, useRef } from 'react'
import {
  fetchClientes,
  fetchDashboardKPIs,
  bankSync,
  exportContabilidade,
  createCliente,
  updateCliente,
  deleteCliente,
  type Cliente,
  type DashboardKPIs,
} from './App'
import { Toast, type ToastType } from './Toast'
import { getSupabaseClient } from './lib/supabase'

function Badge({ status }: { status: 'pago' | 'pendente' | 'atrasado' }) {
  const styles: Record<string, string> = {
    pago: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    pendente: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    atrasado: 'bg-red-500/20 text-red-400 border-red-500/30',
  }
  const labels: Record<string, string> = { pago: 'Pago', pendente: 'Pendente', atrasado: 'Atrasado' }
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${styles[status] || ''}`}
    >
      {labels[status] || status}
    </span>
  )
}

function TableSkeleton() {
  const rows = 6
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/50 shadow">
      <table className="min-w-full divide-y divide-zinc-800">
        <thead>
          <tr>
            {['Nome', 'Documento', 'Mensalidade', 'Vencimento', 'Status'].map((h) => (
              <th
                key={h}
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800">
          {Array.from({ length: rows }).map((_, i) => (
            <tr key={i}>
              <td className="px-4 py-3"><span className="skeleton inline-block h-4 w-32" /></td>
              <td className="px-4 py-3"><span className="skeleton inline-block h-4 w-24" /></td>
              <td className="px-4 py-3"><span className="skeleton inline-block h-4 w-20" /></td>
              <td className="px-4 py-3"><span className="skeleton inline-block h-4 w-16" /></td>
              <td className="px-4 py-3"><span className="skeleton inline-block h-6 w-16 rounded-md" /></td>
              <td className="px-4 py-3"><span className="skeleton inline-block h-6 w-20 rounded-md" /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function KPISkeleton() {
  return (
    <div className="mb-8 grid gap-4 sm:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 shadow-sm">
          <span className="skeleton inline-block h-4 w-24 rounded" />
          <span className="skeleton mt-3 inline-block h-8 w-28 rounded" />
          <span className="skeleton mt-2 inline-block h-3 w-12 rounded" />
        </div>
      ))}
    </div>
  )
}

function Spinner() {
  return (
    <svg
      className="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}

export function Dashboard() {
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [toast, setToast] = useState<{ type: ToastType; message: string } | null>(null)
  const dismissToast = useCallback(() => setToast(null), [])

  const [modalOpen, setModalOpen] = useState(false)
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const load = useCallback(async (showLoading = true) => {
    setError(null)
    if (showLoading) setLoading(true)
    try {
      const [clientesData, kpisData] = await Promise.all([
        fetchClientes(),
        fetchDashboardKPIs(),
      ])
      setClientes(clientesData)
      setKpis(kpisData)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar')
    } finally {
      if (showLoading) setLoading(false)
    }
  }, [])

  const loadRef = useRef(load)
  loadRef.current = load

  useEffect(() => {
    load()
  }, [load])

  // Supabase Realtime: atualiza lista e KPIs quando clientes ou transacoes mudam (ex.: cadastro via WhatsApp).
  // Requer VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY no .env e tabelas clientes/transacoes na publicação Realtime (Supabase > Database > Replication).
  useEffect(() => {
    const supabase = getSupabaseClient()
    if (!supabase) return

    const channel = supabase
      .channel('dashboard-db-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'clientes' },
        () => {
          loadRef.current?.(false)
        }
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'transacoes' },
        () => {
          loadRef.current?.(false)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const handleSincronizar = async () => {
    setError(null)
    setMessage(null)
    setSyncing(true)
    try {
      const res = await bankSync()
      setToast({
        type: 'success',
        message: `${res.message} Transações: ${res.transacoes_extrato}. Matches: ${res.matches_criados}.`,
      })
      await load()
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Erro ao sincronizar'
      setToast({ type: 'error', message: msg })
    } finally {
      setSyncing(false)
    }
  }

  const handleExportar = async () => {
    setError(null)
    setExporting(true)
    try {
      const blob = await exportContabilidade()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'contabilidade.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao exportar')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Gestão Financeira Inteligente
          </h1>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleSincronizar}
              disabled={syncing || loading}
              className="inline-flex items-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {syncing && <Spinner />}
              {syncing ? 'Sincronizando…' : 'Sincronizar Santander'}
            </button>
            <button
              type="button"
              onClick={handleExportar}
              disabled={exporting || loading}
              className="inline-flex items-center rounded-lg border border-zinc-600 bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-200 hover:bg-zinc-700 disabled:opacity-50"
            >
              {exporting && <Spinner />}
              Exportar para Contabilidade
            </button>
          </div>
        </header>

        {message && (
          <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            {message}
          </div>
        )}
        {error && (
          <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {toast && (
          <Toast
            type={toast.type}
            message={toast.message}
            onDismiss={dismissToast}
            duration={5000}
          />
        )}

        {loading ? (
          <KPISkeleton />
        ) : kpis ? (
          <div className="mb-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 shadow-sm">
              <p className="text-sm font-medium text-zinc-400">Total Recebido</p>
              <p className="mt-1 text-2xl font-semibold text-white">
                R$ {kpis.total_recebido.toFixed(2)}
              </p>
              <p className="mt-0.5 text-xs text-zinc-500">no mês</p>
            </div>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 shadow-sm">
              <p className="text-sm font-medium text-zinc-400">Notas a Emitir</p>
              <p className="mt-1 text-2xl font-semibold text-amber-400">
                {kpis.notas_a_emitir}
              </p>
              <p className="mt-0.5 text-xs text-zinc-500">pendentes</p>
            </div>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 shadow-sm">
              <p className="text-sm font-medium text-zinc-400">Clientes Inadimplentes</p>
              <p className="mt-1 text-2xl font-semibold text-red-400">
                {kpis.clientes_inadimplentes}
              </p>
              <p className="mt-0.5 text-xs text-zinc-500">atrasados</p>
            </div>
          </div>
        ) : null}

        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-medium text-zinc-200">Clientes</h2>
            <button
              type="button"
              onClick={openNewModal}
              className="inline-flex items-center rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500"
            >
              + Novo Cliente
            </button>
          </div>
          {loading ? (
            <TableSkeleton />
          ) : (
            <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/50 shadow">
              <table className="min-w-full divide-y divide-zinc-800">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Nome
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Documento
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Mensalidade
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Vencimento
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Status
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-zinc-400">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {clientes.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-zinc-500">
                        Nenhum cliente cadastrado.
                      </td>
                    </tr>
                  ) : (
                    clientes.map((c) => (
                      <tr key={c.id} className="hover:bg-zinc-800/50">
                        <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-white">
                          {c.nome}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-zinc-400">
                          {c.documento_cpf_cnpj ?? '–'}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-zinc-300">
                          R$ {c.valor_mensalidade.toFixed(2)}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-zinc-400">
                          Dia {c.dia_vencimento}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3">
                          <Badge status={c.status_pagamento} />
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-right">
                          <div className="flex justify-end gap-2">
                            <button
                              type="button"
                              onClick={() => openEditModal(c)}
                              className="rounded border border-zinc-600 px-2 py-1 text-xs font-medium text-zinc-300 hover:bg-zinc-700"
                            >
                              Editar
                            </button>
                            <button
                              type="button"
                              onClick={() => handleExcluir(c)}
                              disabled={deletingId === c.id}
                              className="rounded border border-red-500/50 px-2 py-1 text-xs font-medium text-red-400 hover:bg-red-500/20 disabled:opacity-50"
                            >
                              {deletingId === c.id ? 'Excluindo…' : 'Excluir'}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <ModalCliente
          open={modalOpen}
          onClose={closeModal}
          editing={editingCliente}
          initial={modalInitial}
          onSubmit={handleSubmitCliente}
          submitting={submitting}
        />
      </div>
    </div>
  )
}
