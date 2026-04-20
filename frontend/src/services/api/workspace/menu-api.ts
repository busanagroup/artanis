import { useQuery } from '@tanstack/react-query'
import { axelorJson } from '@/services/http/axelor-http'
import type { ActionExecResponse, ActionResponse, ActionViewSummary, ApiListResponse, FetchResponse, MenuItem, MetaViewResponse, PermsResponse, QuickAccessSection, RemoveResponse, SaveResponse, SearchResponse, SessionInfoResponse } from '@/types/menu'

export async function fetchAppInfo() {
  const live = await axelorJson<SessionInfoResponse>('/auth/userinfo')
  return live
}

export function useGetAppInfo() {
  return useQuery({
    queryKey: ['app-info'],
    queryFn: fetchAppInfo,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function fetchMenuItems(): Promise<MenuItem[]> {
  const live = await axelorJson<ApiListResponse<MenuItem>>('ws/action/menu/all')
  return live.status === 0 ? live.data : []
}

export function useGetMenuItems() {
  return useQuery({
    queryKey: ['menu-all'],
    queryFn: fetchMenuItems,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function fetchQuickAccess(): Promise<QuickAccessSection[]> {
  const live = await axelorJson<ApiListResponse<QuickAccessSection>>('ws/action/menu/quick')
  return live.status === 0 ? live.data : []
}

export function useGetQuickAccess() {
  return useQuery({
    queryKey: ['menu-quick'],
    queryFn: fetchQuickAccess,
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function fetchActionView(actionName: string): Promise<ActionViewSummary | null> {
  const response = await axelorJson<ActionResponse>(`ws/action/${actionName}`, {
    method: 'POST',
    jsonBody: {
      model: 'com.axelor.meta.db.MetaAction',
      data: {
        context: {},
      },
    },
  })

  if (response.status !== 0) {
    throw new Error(`Action ${actionName} gagal dimuat`)
  }

  return response.data[0]?.view ?? null
}

export function useGetActionView(actionName?: string | null) {
  return useQuery({
    queryKey: ['action-view', actionName],
    queryFn: () => fetchActionView(actionName!),
    enabled: Boolean(actionName),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function fetchMetaView(model: string, limit = 8, signal?: AbortSignal): Promise<Array<Record<string, unknown>>> {
  const response = await axelorJson<MetaViewResponse>(`ws/meta/view`, {
    method: 'POST',
    signal,
    jsonBody: {
      limit,
      offset: 0,
      data: {},
    },
  })

  if (response.status !== 0) {
    throw new Error(`Data model ${model} gagal dimuat`)
  }

  return response.data ?? []
}

export async function fetchModelRecords(model: string, limit = 8): Promise<Array<Record<string, unknown>>> {
  const response = await axelorJson<SearchResponse>(`ws/rest/${model}/search`, {
    method: 'POST',
    jsonBody: {
      limit,
      offset: 0,
      data: {},
    },
  })

  if (response.status !== 0) {
    throw new Error(`Data model ${model} gagal dimuat`)
  }

  return response.data ?? []
}

export function useGetModelRecords(model?: string | null, limit = 8) {
  return useQuery({
    queryKey: ['records', model, limit],
    queryFn: () => fetchModelRecords(model!, limit),
    enabled: Boolean(model),
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function saveModelRecord(model: string, record: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await axelorJson<SaveResponse>(`ws/rest/${model}`, {
    method: 'POST',
    jsonBody: {
      data: record,
    },
  })

  if (response.status !== 0) {
    throw new Error(`Gagal menyimpan data model ${model}`)
  }

  return response.data?.[0] ?? {}
}

export async function fetchModelRecord(model: string, id: number): Promise<Record<string, unknown> | null> {
  const response = await axelorJson<FetchResponse>(`ws/rest/${model}/${id}/fetch`, {
    method: 'POST',
    jsonBody: {},
  })

  if (response.status !== 0) {
    throw new Error(`Gagal mengambil detail record ${model}#${id}`)
  }

  return response.data?.[0] ?? null
}

export function useGetModelRecord(model?: string | null, id?: number | null, enabled = true) {
  return useQuery({
    queryKey: ['fetch-record', model, id],
    queryFn: () => fetchModelRecord(model!, id!),
    enabled: enabled && Boolean(model) && typeof id === 'number',
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function fetchModelPerms(model: string, id?: number): Promise<Record<'read' | 'write' | 'create' | 'remove' | 'export', boolean>> {
  const params = new URLSearchParams()
  if (typeof id === 'number' && Number.isFinite(id)) {
    params.set('id', String(id))
  }

  const suffix = params.size ? `?${params}` : ''
  const response = await axelorJson<PermsResponse>(`ws/rest/${model}/perms${suffix}`, {
    method: 'GET',
  })

  if (response.status !== 0) {
    throw new Error(`Gagal mengambil perms ${model}`)
  }

  const values = (response.data ?? []).map((value) => value.toLowerCase())
  return {
    read: values.includes('read'),
    write: values.includes('write'),
    create: values.includes('create'),
    remove: values.includes('remove'),
    export: values.includes('export'),
  }
}

export function useGetModelPerms(model?: string | null, id?: number | null) {
  return useQuery({
    queryKey: ['perms', model, id],
    queryFn: () => fetchModelPerms(model!, id ?? undefined),
    enabled: Boolean(model),
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 1,
  })
}

export async function executeModelAction(input: {
  action: string
  model: string
  context?: Record<string, unknown>
}) {
  const response = await axelorJson<ActionExecResponse>('ws/action', {
    method: 'POST',
    jsonBody: {
      action: input.action,
      model: input.model,
      data: {
        context: input.context ?? {},
      },
    },
  })

  if (response.status !== 0) {
    throw new Error(response.errors ? Object.values(response.errors).join(', ') : `Action ${input.action} gagal`)
  }

  return response.data ?? []
}

export async function deleteModelRecords(
  model: string,
  records: Array<{ id: number; version?: number }>,
): Promise<number> {
  const response = await axelorJson<RemoveResponse>(`ws/rest/${model}/removeAll`, {
    method: 'POST',
    jsonBody: { records },
  })

  if (response.status !== 0) {
    throw new Error(`Gagal menghapus data model ${model}`)
  }

  return response.data?.length ?? 0
}
