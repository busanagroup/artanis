import { EditOutlined } from '@ant-design/icons'
import { Button, Card, Empty, Tag, Typography } from 'antd'
import type { RecordItem } from './list-view'

const { Text } = Typography

type CardViewProps = {
  records: RecordItem[]
  visibleColumns: string[]
  selectedRecordId?: string
  canEdit: boolean
  getRecordTitle: (record: RecordItem) => string
  onEditRecord: (record: RecordItem) => void
  onSelectRecord: (record: RecordItem) => void
}

export function CardView({
  records,
  visibleColumns,
  selectedRecordId,
  canEdit,
  getRecordTitle,
  onEditRecord,
  onSelectRecord,
}: CardViewProps) {
  if (!records.length) {
    return <Empty description="Belum ada data untuk ditampilkan." className="py-16" />
  }

  return (
    <div className="grid gap-4 p-5 sm:grid-cols-2 2xl:grid-cols-3">
      {records.map((record, index) => {
        const selected = String(record.id ?? '') === String(selectedRecordId ?? '')

        return (
          <Card
            key={String(record.id ?? index)}
            hoverable
            bordered={false}
            className={`!rounded-[24px] !border !shadow-none transition-all ${
              selected
                ? '!border-[#9dacff] !bg-[linear-gradient(180deg,#f4f3ff_0%,#ffffff_100%)]'
                : '!border-[#e7edf7] !bg-white'
            }`}
            bodyStyle={{ padding: 20 }}
            onClick={() => onSelectRecord(record)}
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div className="min-w-0">
                <Tag color={selected ? 'purple' : 'blue'} className="!mb-3 !rounded-full !px-3 !py-1">
                  {selected ? 'Selected' : 'Record'}
                </Tag>
                <p className="truncate text-base font-semibold text-[#2a4278]">{getRecordTitle(record)}</p>
              </div>

              <Button
                type="text"
                shape="circle"
                icon={<EditOutlined />}
                disabled={!canEdit}
                onClick={(event) => {
                  event.stopPropagation()
                  onEditRecord(record)
                }}
              />
            </div>

            <div className="space-y-3">
              {visibleColumns.slice(0, 4).map((column) => (
                <div key={`${String(record.id ?? index)}-${column}`} className="rounded-2xl bg-[#f7f9ff] px-3 py-2.5">
                  <Text className="!text-[11px] !font-semibold !uppercase !tracking-[0.12em] !text-[#8a96b3]">{column}</Text>
                  <p className="mt-1 truncate text-sm text-[#425381]">{String(record[column] ?? '-')}</p>
                </div>
              ))}
            </div>
          </Card>
        )
      })}
    </div>
  )
}
