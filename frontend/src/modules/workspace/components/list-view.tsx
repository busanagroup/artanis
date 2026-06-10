import { useMemo } from 'react'
import type { ReactNode } from 'react'
import { Button, Tooltip } from 'antd'
import { Pencil, Trash2 } from 'lucide-react'
import { filterIcon } from '@progress/kendo-svg-icons'
import { Grid, GridColumn as Column, GridNoRecords, type GridCellProps } from '@progress/kendo-react-grid'
import { ColumnMenu } from './filter-component'
import type { WorkspaceViewItem } from '@/types/menu'
import { getViewItemLabel } from '../hooks/controllers/workspace-utils'

export type RecordItem = Record<string, unknown>

export type GridColumnDef = {
  name: string
  title: string
  width?: number
}

type ListViewBaseProps = {
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

type ListViewProps = ListViewBaseProps & {
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

type EmptyListViewProps = ListViewBaseProps

function WorkspaceGrid({
  records,
  columns,
  showActions = true,
  height = 500,
  selectedRecordId,
  canEdit,
  canRemove,
  rowActions = [],
  renderCell = (column, value) => String(value ?? '-') ?? column,
  onEditRecord = () => undefined,
  onDeleteRecord = () => undefined,
  onSelectRecord = () => undefined,
  onRunAction,
  emptyDescription = 'There is no data available',
}: {
  records: RecordItem[]
  columns: GridColumnDef[]
  selectedRecordId?: string
  height?: number | string
  canEdit?: boolean
  canRemove?: boolean
  showActions?: boolean
  rowActions?: WorkspaceViewItem[]
  renderCell?: (column: string, value: unknown) => ReactNode
  onEditRecord?: (record: RecordItem) => void
  onDeleteRecord?: (record: RecordItem) => void
  onSelectRecord?: (record: RecordItem) => void
  onRunAction?: (actionName: string, record: RecordItem) => void | Promise<void>
  emptyDescription?: string
}) {
  const selectionField = '__selected'
  const actionField = '__actions'

  const gridData = useMemo(
    () =>
      records.map((record) => ({
        ...record,
        [selectionField]: String(record.id ?? '') === String(selectedRecordId ?? ''),
        [actionField]: '',
      })),
    [records, selectedRecordId],
  )

  const CommandCell = (props: GridCellProps) => (
    <td className={`${props.className ?? ''} whitespace-nowrap px-2 py-2`}>
      <div className="flex items-center gap-1">
        {rowActions.map((action) => {
          const actionName = action.onClick
          const label = getViewItemLabel(action)
          return (
            <Tooltip key={`${action.name ?? actionName}`} title={label}>
              <Button
                type="text"
                size="small"
                onClick={(event) => {
                  event.stopPropagation()
                  if (actionName) {
                    void onRunAction?.(actionName, props.dataItem as RecordItem)
                  }
                }}
                className="!px-2 !text-slate-500"
                disabled={!actionName || !onRunAction}
              >
                {action.icon ? action.icon : label}
              </Button>
            </Tooltip>
          )
        })}
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation()
            onEditRecord(props.dataItem as RecordItem)
          }}
          disabled={!canEdit}
          className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          title="Edit row"
        >
          <Pencil className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation()
            onDeleteRecord(props.dataItem as RecordItem)
          }}
          disabled={!canRemove}
          className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          title="Delete row"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </td>
  )

  return (
    <div className="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" style={{ height }}>
      <Grid
        data={gridData}
        style={{ height: '100%' }}
        className="h-full w-full"
        dataItemKey="id"
        autoProcessData={true}
        sortable={true}
        pageable={true}
        resizable={true}
        groupable={true}
        defaultGroup={[]}
        editable={true}
        defaultSkip={0}
        defaultTake={10}
        columnMenuIcon={filterIcon}
        onRowClick={(event) => onSelectRecord(event.dataItem as RecordItem)}
      >
        <GridNoRecords>
          <div className="flex h-full min-h-[300px] flex-col items-center justify-center gap-2 py-8 text-center">
            <div className="text-base font-medium text-slate-600">
              No data available
            </div>
            <div className="max-w-sm text-sm text-slate-400">
              {emptyDescription}
            </div>
          </div>
        </GridNoRecords>
        {showActions ? (
          <Column
            field={actionField}
            title="Actions"
            filterable={false}
            width={Math.max(120, 120 + rowActions.length * 72)}
            cells={{ data: CommandCell }}
          />
        ) : null}
        {columns.map((column) => {
          const cell = (props: GridCellProps) => (
            <td className={`${props.className ?? ''} whitespace-nowrap px-3 py-2 text-[#3f4c7c]`}>
              {renderCell(column.name, (props.dataItem as RecordItem)[column.name])}
            </td>
          )
          return (
            <Column
              key={column.name}
              columnMenu={ColumnMenu}
              field={column.name}
              title={column.title}
              width={column.width ?? Math.max(120, Math.min(220, column.title.length * 12))}
              cells={{ data: cell }}
            />
          )
        })}
      </Grid>
    </div>
  )
}

export function ListView(props: ListViewProps) {
  return <WorkspaceGrid {...props} />
}

export function EmptyListView(props: EmptyListViewProps) {
  return <WorkspaceGrid records={[]} showActions={false} {...props} />
}
