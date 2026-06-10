import type { AppTab } from '@/store/app-store'
import type { MenuItem, WorkspaceViewDefinition, WorkspaceViewItem } from '@/types/menu'

export type FilterOperator = 'contains' | 'equals' | 'startsWith' | 'endsWith' | 'isEmpty' | 'isNotEmpty'

export type FilterClause = {
  operator: FilterOperator
  value: string
}

export type ColumnFilter = {
  mode: 'AND' | 'OR'
  clauses: [FilterClause, FilterClause?]
}

export type MenuNode = {
  item: MenuItem
  children: MenuNode[]
}

export function normalizeViewMode(viewType?: string | null) {
  if (!viewType) return 'list'
  const value = viewType.toLowerCase()
  if (value === 'grid') return 'list'
  if (value === 'card') return 'cards'
  return value
}

export function normalizeWorkspaceViewKind(viewKind?: string | null) {
  if (!viewKind) return 'list'
  const value = viewKind.toLowerCase()
  if (value === 'grid') return 'list'
  if (value === 'card' || value === 'cards') return 'cards'
  if (value === 'form') return 'form'
  return 'list'
}

export function getModesFromAction(actionView: { viewType?: string; views?: Array<{ type: string }> } | null | undefined) {
  if (!actionView) return ['list']
  const direct = normalizeViewMode(actionView.viewType)
  const fromViews = (actionView.views ?? []).map((view) => normalizeViewMode(view.type))
  const all = [direct, ...fromViews].filter((mode) => mode === 'list' || mode === 'cards' || mode === 'form')
  return Array.from(new Set(all.length ? all : ['list']))
}

export function buildMenuTree(items: MenuItem[]) {
  const visibleItems = items.filter((item) => !item.hidden)
  const byName = new Map<string, MenuNode>()

  for (const item of visibleItems) {
    byName.set(item.name, { item, children: [] })
  }

  const roots: MenuNode[] = []
  for (const node of byName.values()) {
    if (node.item.parent && byName.has(node.item.parent)) {
      byName.get(node.item.parent)!.children.push(node)
    } else {
      roots.push(node)
    }
  }

  const sortNodes = (nodes: MenuNode[]) => {
    nodes.sort((left, right) => left.item.order - right.item.order)
    nodes.forEach((node) => sortNodes(node.children))
  }

  sortNodes(roots)
  return roots
}

export function filterMenuTree(nodes: MenuNode[], search: string): MenuNode[] {
  if (!search.trim()) {
    return nodes
  }

  const q = search.toLowerCase()
  const walk = (node: MenuNode): MenuNode | null => {
    const children = node.children.map(walk).filter((child): child is MenuNode => child !== null)
    const titleMatch = node.item.title.toLowerCase().includes(q)
    const actionMatch = (node.item.action ?? '').toLowerCase().includes(q)

    if (titleMatch || actionMatch || children.length > 0) {
      return { ...node, children }
    }
    return null
  }

  return nodes.map(walk).filter((node): node is MenuNode => node !== null)
}

export function collectExpandableNodeNames(nodes: MenuNode[]) {
  const names = new Set<string>()
  const visit = (node: MenuNode) => {
    if (node.children.length > 0) {
      names.add(node.item.name)
      node.children.forEach(visit)
    }
  }

  nodes.forEach(visit)
  return names
}

export function buildParentMap(items: MenuItem[]) {
  return items.reduce<Record<string, string | undefined>>((acc, item) => {
    acc[item.name] = item.parent
    return acc
  }, {})
}

export function collectAncestorNames(name: string, parentMap: Record<string, string | undefined>) {
  const names: string[] = []
  let current = parentMap[name]

  while (current) {
    names.push(current)
    current = parentMap[current]
  }

  return names
}

export function humanizeFieldName(value: string) {
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[._-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^./, (char) => char.toUpperCase())
}

export function extractViewColumns(view?: WorkspaceViewDefinition | null) {
  return (view?.items ?? [])
    .filter((item): item is WorkspaceViewItem => item.defkind === 'field' && !item.hidden && Boolean(item.name))
    .map((item) => {
      const name = String(item.name)
      const rawWidth = typeof item.width === 'string' ? Number.parseInt(item.width, 10) : undefined
      return {
        name,
        title: item.title || humanizeFieldName(name),
        width: Number.isFinite(rawWidth) ? rawWidth : undefined,
      }
    })
}

export function extractViewButtons(view?: WorkspaceViewDefinition | null) {
  return (view?.items ?? []).filter(
    (item): item is WorkspaceViewItem => item.defkind === 'button' && !item.hidden && Boolean(item.onClick),
  )
}

export function extractViewToolbarButtons(view?: WorkspaceViewDefinition | null) {
  return (view?.toolbar ?? []).filter(
    (item): item is WorkspaceViewItem => item.defkind === 'button' && !item.hidden && Boolean(item.onClick),
  )
}

export function getViewItemLabel(item: WorkspaceViewItem) {
  return item.title || item.name || item.onClick || 'Action'
}

export function parseHashRoute(hash: string) {
  const cleaned = hash.replace(/^#\/?/, '')
  const [namespace, actionKey, viewMode = 'list'] = cleaned.split('/')

  if (namespace !== 'ds' || !actionKey) {
    return null
  }

  return {
    actionKey: decodeURIComponent(actionKey),
    viewMode: normalizeViewMode(viewMode),
  }
}

export function toHashRoute(tab: AppTab | null, tabIndex: number, modeOverride?: string) {
  if (!tab) {
    return '#/'
  }

  const mode = modeOverride || tab.viewMode || 'list'
  return `#/ds/${encodeURIComponent(tab.actionKey)}/${mode}/${tabIndex}`
}

export function renderCell(column: string, value: unknown) {
  if (column.toLowerCase().includes('color') && typeof value === 'string' && value.trim()) {
    return <span className="rounded-full bg-slate-800 px-2 py-1 text-xs font-semibold text-white">{value}</span>
  }

  if (typeof value === 'number') {
    return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
  }

  return String(value ?? '-')
}

export function getRecordTitle(record: Record<string, unknown>) {
  const names = ['name', 'fullName', 'title', 'subject']
  for (const name of names) {
    if (typeof record[name] === 'string' && record[name]) {
      return String(record[name])
    }
  }
  return String(record.id ?? 'Record')
}
