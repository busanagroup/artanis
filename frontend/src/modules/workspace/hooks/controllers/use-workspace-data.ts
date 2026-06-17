import { useMemo, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { useAppActions, useAppState } from '@/store/app-store'
import { executeModelAction, useGetActionView, useGetMetaView, useGetModelRecords } from '@/services/api/workspace/menu-api'
import { message } from 'antd'
import type { ColumnFilter, FilterClause } from './workspace-utils'
import {
  extractViewColumns,
  extractViewButtons,
  extractViewToolbarButtons,
  getModesFromAction,
  normalizeWorkspaceViewKind,
} from './workspace-utils'

type AppState = ReturnType<typeof useAppState>

export function useWorkspaceDataController({ state }: { state: AppState; actions: ReturnType<typeof useAppActions> }) {
  const queryClient = useQueryClient()
  const [selectedRecordByTab, setSelectedRecordByTab] = useState<Record<string, string>>({})
  const [columnFiltersByTab, setColumnFiltersByTab] = useState<Record<string, Record<string, ColumnFilter>>>({})
  const activeTab = useMemo(() => {
    if (!state.activeTabId) return null
    return state.openTabs.find((tab) => tab.id === state.activeTabId) ?? null
  }, [state.activeTabId, state.openTabs])

  const activeTabIndex = useMemo(() => {
    if (!activeTab) return 1
    const index = state.openTabs.findIndex((tab) => tab.id === activeTab.id)
    return index >= 0 ? index + 1 : 1
  }, [activeTab, state.openTabs])

  const activeActionQuery = useGetActionView(activeTab?.actionKey)

  const activeView = useMemo(() => {
    const action = activeActionQuery.data

    if (!action?.views?.length) return null

    const view =
      action.views.find((v) => v.type === action.type) ??
      action.views[0]

    return {
      service: action.service,
      name: view.name ?? undefined,
      type: view.type ?? undefined,
    }
  }, [activeActionQuery.data])

  const activeMetaViewQuery = useGetMetaView({
    service: activeView?.service,
    name: activeView?.name,
    type: activeView?.type,
  })

  const activeMetaView = activeMetaViewQuery.data ?? null

  const activeModes = useMemo(() => getModesFromAction(activeActionQuery.data), [activeActionQuery.data])

  const activeRecordsQuery = useGetModelRecords(activeActionQuery.data?.service, 40)

  const viewColumns = useMemo(() => extractViewColumns(activeMetaView), [activeMetaView])

  const viewButtons = useMemo(() => extractViewButtons(activeMetaView), [activeMetaView])

  const viewToolbarButtons = useMemo(() => extractViewToolbarButtons(activeMetaView), [activeMetaView])

  const activeMetaViewKind = typeof activeMetaView?.defkind === 'string' ? activeMetaView.defkind : undefined

  const activeViewKind = useMemo(
    () => normalizeWorkspaceViewKind(activeMetaViewKind ?? activeTab?.viewMode ?? activeActionQuery.data?.viewType),
    [activeActionQuery.data?.viewType, activeMetaViewKind, activeTab?.viewMode],
  )

  const visibleColumns = useMemo(() => viewColumns.map((column) => column.name), [viewColumns])

  const activeColumnFilters = useMemo(() => {
    if (!activeTab) return {}
    return columnFiltersByTab[activeTab.id] ?? {}
  }, [activeTab, columnFiltersByTab])

  const filteredRecords = useMemo(() => {
    const records = activeRecordsQuery.data ?? []
    const entries = Object.entries(activeColumnFilters)
    if (!entries.length) return records

    const hasValue = (value: unknown) => String(value ?? '').trim().length > 0
    const normalize = (value: unknown) => String(value ?? '').toLowerCase()

    const runClause = (recordValue: unknown, clause: FilterClause) => {
      const left = normalize(recordValue)
      const right = clause.value.trim().toLowerCase()
      switch (clause.operator) {
        case 'contains':
          return right ? left.includes(right) : true
        case 'equals':
          return right ? left === right : true
        case 'startsWith':
          return right ? left.startsWith(right) : true
        case 'endsWith':
          return right ? left.endsWith(right) : true
        case 'isEmpty':
          return !hasValue(recordValue)
        case 'isNotEmpty':
          return hasValue(recordValue)
      }
    }

    const isClauseActive = (clause?: FilterClause) => {
      if (!clause) return false
      return clause.operator === 'isEmpty' || clause.operator === 'isNotEmpty' || clause.value.trim().length > 0
    }

    return records.filter((record) => {
      return entries.every(([column, filter]) => {
        const [first, second] = filter.clauses
        const firstActive = isClauseActive(first)
        const secondActive = isClauseActive(second)
        if (!firstActive && !secondActive) return true

        const firstResult = firstActive ? runClause(record[column], first) : true
        if (!secondActive) return firstResult

        const secondResult = runClause(record[column], second!)
        return filter.mode === 'AND' ? firstResult && secondResult : firstResult || secondResult
      })
    })
  }, [activeColumnFilters, activeRecordsQuery.data])

  const selectedRecord = useMemo(() => {
    if (!activeTab || !filteredRecords.length) return null

    const selectedId = selectedRecordByTab[activeTab.id]
    const found = filteredRecords.find((record) => String(record.id ?? '') === selectedId)
    return found ?? filteredRecords[0]
  }, [activeTab, filteredRecords, selectedRecordByTab])

  const selectedRecordId = useMemo(() => {
    const value = selectedRecord?.id
    const asNumber = typeof value === 'number' ? value : Number(value)
    return Number.isFinite(asNumber) ? asNumber : null
  }, [selectedRecord])

  const selectedRecordKey = useMemo(() => {
    if (!activeTab) return null
    return selectedRecordByTab[activeTab.id] ?? null
  }, [activeTab, selectedRecordByTab])

  // Debug: log filtered record ids and selected key for active tab to diagnose selection mismatch
  // eslint-disable-next-line no-console
  console.debug('useWorkspaceDataController.debug', {
    activeTabId: activeTab?.id,
    filteredRecordIds: filteredRecords.map((r) => r.id),
    selectedKeyForTab: activeTab ? selectedRecordByTab[activeTab.id] : null,
    selectedRecordResolved: selectedRecord,
  })

  function selectRecord(record: Record<string, unknown>) {
    console.log('useWorkspaceDataController.selectRecord', { activeTabId: activeTab?.id, recordId: record?.id })
    if (!activeTab) return
    setSelectedRecordByTab((prev) => ({ ...prev, [activeTab.id]: String(record.id ?? '') }))
  }

  function setColumnFilter(column: string, filter: ColumnFilter | null) {
    if (!activeTab) return
    setColumnFiltersByTab((prev) => {
      const current = prev[activeTab.id] ?? {}
      const next = { ...current }
      if (filter) next[column] = filter
      else delete next[column]
      return {
        ...prev,
        [activeTab.id]: next,
      }
    })
  }

  async function refreshCurrentData() {
    if (!activeActionQuery.data?.service) return
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['records', activeActionQuery.data.model] }),
      queryClient.invalidateQueries({ queryKey: ['fetch-record', activeActionQuery.data.model] }),
      queryClient.invalidateQueries({ queryKey: ['perms', activeActionQuery.data.model] }),
      queryClient.invalidateQueries({ queryKey: ['action-view', activeTab?.actionKey] }),
      queryClient.invalidateQueries({ queryKey: ['meta-view'] }),
    ])
  }

  async function runViewAction(actionName: string, context: Record<string, unknown> = {}) {
    const service = activeActionQuery.data?.service
    // Debug: log runViewAction calls so we can see service/action/context
    // eslint-disable-next-line no-console
    console.debug('useWorkspaceDataController.runViewAction', { service, actionName, context })

    if (!service || !actionName) return
    const hide = message.loading({ content: 'Executing action...', key: 'runViewAction' })
    try {
      const res = await executeModelAction({
        service,
        name: actionName,
        context,
      })
      hide()
      message.success({ content: 'Action executed', key: 'runViewAction', duration: 2 })
      // Debug: log response
      // eslint-disable-next-line no-console
      console.debug('useWorkspaceDataController.runViewAction.response', res)
      return res
    } catch (err) {
      hide()
      // eslint-disable-next-line no-console
      console.error('runViewAction failed', err)
      message.error({ content: (err as Error)?.message ?? 'Action failed', key: 'runViewAction', duration: 4 })
      throw err
    }
  }

  return {
    queryClient,
    activeTab,
    activeTabIndex,
    activeActionQuery,
    activeModes,
    activeRecordsQuery,
    filteredRecords,
    visibleColumns,
    selectedRecord,
    selectedRecordId,
    selectRecord,
    selectedRecordKey,
    activeColumnFilters,
    setColumnFilter,
    refreshCurrentData,
    activeMetaViewQuery,
    activeMetaView,
    activeViewKind,
    // viewFields,
    viewColumns,
    viewButtons,
    viewToolbarButtons,
    runViewAction,
    canCreate: true,
    canEdit: true,
    canRemove: true,
  }
}
