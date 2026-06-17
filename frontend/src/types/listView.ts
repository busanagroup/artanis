import type { ReactNode } from "react"
import type { WorkspaceViewItem } from "./menu"
import type { ICellRendererParams } from "ag-grid-community"

export type RecordItem = Record<string, unknown>

export type GridColumnDef = {
    name: string
    title: string
    width?: number
}

export type ListViewBaseProps = {
    columns: GridColumnDef[]
    showActions?: boolean
    height?: number | string
    canEdit?: boolean
    canRemove?: boolean
    rowActions?: WorkspaceViewItem[]
    renderCell?: (column: string, value: unknown) => ReactNode
    onEditRecord?: (record: RecordItem) => void
    onDeleteRecord?: (record: RecordItem) => void
    onSelectRecord?: (record: RecordItem) => void
    onRunAction?: (actionName: string, record: RecordItem) => void | Promise<void>
    emptyDescription?: string
}

export type ListViewProps = ListViewBaseProps & {
    records: RecordItem[]
    selectedRecordId?: string
    height?: number | string
    canEdit: boolean
    canRemove: boolean
    renderCell: (column: string, value: unknown) => ReactNode
    onEditRecord: (record: RecordItem) => void
    onDeleteRecord: (record: RecordItem) => void
    onSelectRecord: (record: RecordItem) => void
}

export type EmptyListViewProps = ListViewBaseProps

export type ValueCellRendererParams = ICellRendererParams<RecordItem> & {
    columnName: string
    renderCell: (column: string, value: unknown) => ReactNode
}

export type ActionCellRendererParams = ICellRendererParams<RecordItem> & {
    canEdit: boolean
    canRemove: boolean
    rowActions: WorkspaceViewItem[]
    onEditRecord: (record: RecordItem) => void
    onDeleteRecord: (record: RecordItem) => void
    onRunAction?: (actionName: string, record: RecordItem) => void | Promise<void>
}