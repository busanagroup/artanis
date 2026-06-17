import { useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { AgGridProvider, AgGridReact } from 'ag-grid-react'
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
  type GridApi,
  type GridReadyEvent,
  themeQuartz,
} from 'ag-grid-community'
import type { WorkspaceViewItem } from '@/types/menu'

import type { ActionCellRendererParams, EmptyListViewProps, GridColumnDef, ListViewProps, RecordItem, ValueCellRendererParams } from '@/types/listView'
ModuleRegistry.registerModules([AllCommunityModule])


function ValueCellRenderer(params: ValueCellRendererParams) {
  return <div className="truncate">{params.renderCell(params.columnName, params.value)}</div>
}



function WorkspaceGrid({
  records,
  columns,
  showActions = true,
  height = 500,
  selectedRecordId,
  renderCell = (_, value) => String(value ?? '-'),
  onSelectRecord = () => { },
}: {
  records: RecordItem[]
  columns: GridColumnDef[]
  selectedRecordId?: string
  height?: number | string
  showActions?: boolean
  renderCell?: (column: string, value: unknown) => ReactNode
  onEditRecord?: (record: RecordItem) => void
  onDeleteRecord?: (record: RecordItem) => void
  onSelectRecord?: (record: RecordItem) => void
  onRunAction?: (actionName: string, record: RecordItem) => void | Promise<void>
  emptyDescription?: string
}) {
  const apiRef = useRef<GridApi<RecordItem> | null>(null)

  const columnDefs = useMemo<ColDef<RecordItem>[]>(() => {
    const valueColumns = columns.map<ColDef<RecordItem>>((column) => ({
      field: column.name,
      headerName: column.title,
      width: column.width,
      minWidth: column.width ?? Math.max(120, Math.min(220, column.title.length * 12)),
      flex: column.width ? undefined : 1,
      sortable: true,
      filter: 'agTextColumnFilter',
      floatingFilter: true,
      resizable: true,
      cellRenderer: ValueCellRenderer,
      cellRendererParams: {
        columnName: column.name,
        renderCell,
      },
      cellClass: 'workspace-grid-cell',
      tooltipValueGetter: (params) => String(params.value ?? '-'),
      wrapText: false,
      suppressHeaderMenuButton: false,
      suppressMovable: false,
    }))

    return valueColumns
  }, [columns, renderCell])

  const rowData = useMemo(
    () =>
      records.map((record) => ({
        ...record,
        __selected: String(record.id ?? '') === String(selectedRecordId ?? ''),
      })),
    [records, selectedRecordId],
  )

  useEffect(() => {
    apiRef.current?.redrawRows()
  }, [rowData, selectedRecordId])

  return (
    <div className="w-full" style={{ height }}>
      <div className="h-full w-full">
        <AgGridProvider modules={[AllCommunityModule]}>
          <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
            <div style={{ flex: 1 }}>
              <AgGridReact<RecordItem>
                rowData={rowData}
                columnDefs={columnDefs}
                theme={themeQuartz}
                sideBar
                defaultColDef={{
                  sortable: true,
                  resizable: true,
                  filter: 'agTextColumnFilter',
                  floatingFilter: true,
                  wrapText: false,
                  autoHeight: false,
                  suppressHeaderMenuButton: false,
                  tooltipValueGetter: (params) => String(params.value ?? '-'),
                }}
                getRowId={(params) => String(params.data.id ?? '')}
                getRowClass={(params) =>
                  String(params.data?.id ?? '') === String(selectedRecordId ?? '')
                    ? 'workspace-grid-row-selected'
                    : undefined
                }
                onGridReady={(event: GridReadyEvent<RecordItem>) => {
                  apiRef.current = event.api
                }}
                onRowClicked={(event) => {
                  if (event.data) {
                    onSelectRecord(event.data)
                  }
                }}
                pagination
                paginationPageSize={10}
                paginationPageSizeSelector={[10, 25, 50]}
                suppressCellFocus
                rowHeight={52}
                headerHeight={48}
                rowSelection={{
                  mode: 'singleRow',
                  enableClickSelection: true,
                  enableSelectionWithoutKeys: true,
                  checkboxes: false,
                }}
                suppressContextMenu={false}
                animateRows
              />
            </div>
          </div>
        </AgGridProvider>
      </div>
    </div>
  )
}

export function ListView(props: ListViewProps) {
  return <WorkspaceGrid {...props} />
}

export function EmptyListView(props: EmptyListViewProps) {
  return <WorkspaceGrid records={[
    {
      "id": "1",
      "fullName": "John Doe",
      "email": "john.doe@example.com",
      "department": "IT",
      "status": "Active",
      "action": "Approve"
    },
    {
      "id": "2",
      "fullName": "Jane Smith",
      "email": "jane.smith@example.com",
      "department": "Finance",
      "status": "Active"
    },
    {
      "id": "3",
      "fullName": "Michael Johnson",
      "email": "michael.johnson@example.com",
      "department": "HR",
      "status": "Inactive"
    },
    {
      "id": "4",
      "fullName": "Sarah Williams",
      "email": "sarah.williams@example.com",
      "department": "Sales",
      "status": "Active"
    },
    {
      "id": "5",
      "fullName": "David Brown",
      "email": "david.brown@example.com",
      "department": "Operations",
      "status": "Active"
    },
    {
      "id": "6",
      "fullName": "Emily Davis",
      "email": "emily.davis@example.com",
      "department": "Marketing",
      "status": "Inactive"
    },
    {
      "id": "7",
      "fullName": "Robert Wilson",
      "email": "robert.wilson@example.com",
      "department": "IT",
      "status": "Active"
    },
    {
      "id": "8",
      "fullName": "Lisa Anderson",
      "email": "lisa.anderson@example.com",
      "department": "Finance",
      "status": "Active"
    },
    {
      "id": "9",
      "fullName": "James Taylor",
      "email": "james.taylor@example.com",
      "department": "HR",
      "status": "Inactive"
    },
    {
      "id": "10",
      "fullName": "Olivia Martinez",
      "email": "olivia.martinez@example.com",
      "department": "Sales",
      "status": "Active"
    }
  ]} showActions={true} {...props} />
}
