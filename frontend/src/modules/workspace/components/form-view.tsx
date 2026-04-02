import { Alert, Button, Card, Input, Typography } from 'antd'
import type { RecordItem } from './list-view'

const { Text, Title } = Typography

export type FormIntent = 'view' | 'create' | 'edit'

type FormViewProps = {
  formIntent: FormIntent
  formRecord: RecordItem
  isSaving: boolean
  saveErrorMessage: string | null
  getRecordTitle: (record: RecordItem) => string
  onSave: () => void
  onCancel: () => void
  onUpdateField: (fieldName: string, nextValue: string) => void
}

export function FormView({
  formIntent,
  formRecord,
  isSaving,
  saveErrorMessage,
  getRecordTitle,
  onSave,
  onCancel,
  onUpdateField,
}: FormViewProps) {
  return (
    <div className="min-h-[520px] bg-[linear-gradient(180deg,#fbfcff_0%,#f7f9fd_100%)] p-5">
      <div className="mb-5 flex flex-col gap-4 rounded-[24px] border border-[#e5ebf6] bg-white px-5 py-5 shadow-sm lg:flex-row lg:items-center lg:justify-between">
        <div>
          <Text className="!text-xs !font-semibold !uppercase !tracking-[0.16em] !text-[#8896b3]">
            {formIntent === 'create' ? 'Create Page' : 'Edit Page'}
          </Text>
          <Title level={4} className="!mb-0 !mt-2 !text-[#223d73]">
            {formIntent === 'create' ? 'Create Record' : `Edit ${getRecordTitle(formRecord)}`}
          </Title>
        </div>

        <div className="flex items-center gap-2">
          <Button type="primary" loading={isSaving} onClick={onSave}>
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
          <Button onClick={onCancel}>Cancel</Button>
        </div>
      </div>

      {saveErrorMessage ? (
        <Alert
          type="error"
          showIcon
          message={saveErrorMessage}
          className="!mb-4 !rounded-2xl !border-0 !bg-[#fff2f0]"
        />
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Object.entries(formRecord)
          .filter(([key]) => !key.startsWith('$'))
          .slice(0, 36)
          .map(([key, value]) => {
            const readOnly = ['id', 'version'].includes(key)

            return (
              <Card
                key={key}
                bordered={false}
                className="!rounded-[22px] !border !border-[#e7edf7] !bg-white !shadow-none"
                bodyStyle={{ padding: 18 }}
              >
                <div className="space-y-3">
                  <div>
                    <Text className="!text-xs !font-semibold !uppercase !tracking-[0.12em] !text-[#8a96b3]">{key}</Text>
                    {readOnly ? (
                      <p className="mt-2 text-sm font-medium text-[#314677]">{String(value ?? '-')}</p>
                    ) : null}
                  </div>

                  {!readOnly ? (
                    <Input
                      value={String(value ?? '')}
                      onChange={(event) => onUpdateField(key, event.target.value)}
                      size="large"
                      className="!rounded-xl"
                    />
                  ) : null}
                </div>
              </Card>
            )
          })}
      </div>
    </div>
  )
}
