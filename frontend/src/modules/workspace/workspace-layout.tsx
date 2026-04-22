import type { ReactNode } from 'react'
import {
  AppstoreOutlined,
  ApartmentOutlined,
  EditOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  UserOutlined,
} from '@ant-design/icons'
import {
  Avatar,
  Badge,
  Button,
  Card,
  Drawer,
  Empty,
  Input,
  Space,
  Spin,
  Tag,
  Tooltip,
  Typography,
} from 'antd'
import { NavTabs } from './components/nav-tabs'
import { CardView } from './components/card-view'
import { FormView } from './components/form-view'
import { ListView } from './components/list-view'
import { useWorkspaceController } from './hooks/use-workspace-controller'
import { toHashRoute, type MenuNode } from './hooks/controllers/workspace-utils'
import Icon from "../../../public/icon/artanis.svg"

const { Title, Paragraph, Text } = Typography

function renderMenuTree(params: {
  nodes: MenuNode[]
  depth?: number
  isExpanded: (name: string) => boolean
  isSelected: (name: string) => boolean
  onToggle: (name: string) => void
  onOpen: (node: MenuNode) => void
}): ReactNode {
  const { nodes, depth = 0, isExpanded, isSelected, onToggle, onOpen } = params

  return nodes.map((node) => {
    const hasChildren = node.children.length > 0
    const expanded = isExpanded(node.item.name)
    const selected = isSelected(node.item.name)

    return (
      <div key={node.item.name} className="space-y-2">
        <button
          type="button"
          onClick={() => {
            if (hasChildren) onToggle(node.item.name)
            else onOpen(node)
          }}
          className={`flex w-full items-center justify-between rounded-2xl border px-3 py-2.5 text-left text-sm transition-all ${selected
            ? 'border-[#6a5cff] bg-[linear-gradient(135deg,#6a5cff_0%,#7d4dff_100%)] text-white shadow-[0_14px_34px_rgba(106,92,255,0.22)]'
            : 'border-transparent bg-white text-[#3e507c] hover:border-[#d9e1f2] hover:bg-[#f8faff]'
            }`}
          style={{ marginLeft: depth * 14 }}
        >
          <span className="flex min-w-0 items-center gap-2">
            {hasChildren ? <ApartmentOutlined className="text-[12px]" /> : <AppstoreOutlined className="text-[12px]" />}
            <span className="truncate">{node.item.title}</span>
          </span>

          {hasChildren ? (
            <span className="text-xs">{expanded ? '−' : '+'}</span>
          ) : node.item.hasTag ? (
            <Tag
              bordered={false}
              className={`!m-0 !rounded-full !px-2 !py-0.5 !text-[11px] ${selected ? '!bg-white/20 !text-white' : '!bg-[#eef2ff] !text-[#5766a5]'}`}
            >
              {node.item.tag}
            </Tag>
          ) : null}
        </button>

        {hasChildren && expanded ? (
          <div className="space-y-2">{renderMenuTree({ ...params, nodes: node.children, depth: depth + 1 })}</div>
        ) : null}
      </div>
    )
  })
}

export function WorkspaceLayout() {
  const controller = useWorkspaceController()

  const menuPanel = (
    <div className="flex h-dvh max-h-dvh flex-col overflow-hidden bg-[linear-gradient(180deg,#f8fbff_0%,#eef4ff_100%)]">
      <div className="shrink-0 border-b border-[#dbe4f2] px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center">
            <img src={Icon} alt="artanis-logo" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-base font-semibold text-[#18376d]">Artanis Workspace</p>
          </div>
        </div>
      </div>

      <div className="shrink-0 border-b border-[#dbe4f2] px-4 py-4">
        <Input
          allowClear
          size="large"
          value={controller.menuSearch}
          onChange={(event) => controller.setMenuSearch(event.target.value)}
          placeholder="Cari menu, model, atau fitur..."
          prefix={<SearchOutlined className="text-[#8e9cc0]" />}
          className="!rounded-2xl !border-[#d7e0ef] !bg-white"
        />
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
        <div className="mb-3 flex items-center justify-between px-1">
          <Text className="!text-xs !font-semibold !uppercase !tracking-[0.18em] !text-[#8693b2]">Navigation</Text>
          <Badge count={controller.filteredMenuTree.length} color="#6a5cff" />
        </div>

        {controller.menuQuery.isLoading ? (
          <div className="flex items-center gap-3 rounded-2xl bg-white px-4 py-4 text-sm text-[#6f7f9f] shadow-sm">
            <Spin size="small" />
            <span>Memuat menu workspace...</span>
          </div>
        ) : null}

        {!controller.menuQuery.isLoading && controller.filteredMenuTree.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Menu tidak ditemukan."
            className="rounded-2xl bg-white py-8"
          />
        ) : null}

        <nav className="space-y-2">{renderMenuTree({
          nodes: controller.filteredMenuTree,
          isExpanded: (name) => controller.expandedMenuNames.has(name) || controller.menuSearch.trim().length > 0,
          isSelected: (name) => controller.state.selectedMenuName === name,
          onToggle: controller.toggleMenuExpand,
          onOpen: (node) => controller.openMenuAsTab(node.item),
        })}</nav>
      </div>
    </div>
  )

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f5f8ff_0%,#eef3fb_100%)] text-slate-800">
      <div
        className={`grid min-h-screen grid-cols-1 ${controller.state.sidebarOpen ? 'lg:grid-cols-[300px_1fr]' : 'lg:grid-cols-[0px_1fr]'}`}
      >
        <aside
          className={`sticky top-0 hidden h-dvh max-h-dvh overflow-hidden border-r border-white/70 bg-white/65 backdrop-blur-xl transition-[width,transform,opacity] duration-300 ease-out lg:block ${controller.state.sidebarOpen ? 'w-[300px] translate-x-0 opacity-100' : 'w-0 -translate-x-4 opacity-0 pointer-events-none border-r-0'
            }`}
        >
          {menuPanel}
        </aside>

        <Drawer
          placement="left"
          width={320}
          onClose={() => controller.actions.setSidebarOpen(false)}
          open={controller.state.sidebarOpen}
          rootClassName="lg:hidden"
          styles={{
            body: { padding: 0 },
            content: {
              borderTopRightRadius: 24,
              borderBottomRightRadius: 24,
              overflow: 'hidden',
            },
          }}
          motion={{
            motionAppear: true,
            motionEnter: true,
            motionLeave: true,
            motionDeadline: 300,
          }}
        >
          {menuPanel}
        </Drawer>

        <section className="min-w-0 px-3 py-3 transition-all duration-300 ease-out sm:px-4 sm:py-4">
          <Card
            bordered={false}
            className="overflow-hidden !rounded-[28px] !bg-white/80 !shadow-[0_20px_60px_rgba(111,132,180,0.18)] backdrop-blur"
            bodyStyle={{ padding: 0 }}
          >
            <div className="border-b border-[#e7edf7] bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(246,249,255,0.96)_100%)] px-4 py-4 sm:px-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex items-start gap-3">
                  <Tooltip title={controller.state.sidebarOpen ? 'Sembunyikan menu' : 'Buka menu'}>
                    <Button
                      type="text"
                      shape="circle"
                      size="large"
                      icon={controller.state.sidebarOpen ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
                      onClick={() => controller.actions.setSidebarOpen(!controller.state.sidebarOpen)}
                    />
                  </Tooltip>

                  <div>
                    <Text className="!text-xs !font-semibold !uppercase !tracking-[0.18em] !text-[#8997b6]">Dashboard</Text>
                    <Title level={3} className="!mb-1 !mt-1 !text-[#18376d]">
                      {controller.activeTab?.title ?? 'Workspace Overview'}
                    </Title>
                    <Paragraph className="!mb-0 !text-sm !text-[#7181a3]">
                      {controller.activeTab
                        ? `Kelola data untuk ${controller.activeTab.title} dengan tampilan ${controller.isFormOpen ? 'form' : controller.activeTab.viewMode}.`
                        : 'Pilih menu di sidebar untuk membuka modul dan mulai bekerja.'}
                    </Paragraph>
                  </div>
                </div>

                <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center">
                  <div className="flex items-center gap-3 rounded-2xl border border-[#e3eaf5] bg-white px-3 py-2">
                    <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#e8edff', color: '#4e5bd9' }} />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-[#21396d]">{controller?.profile?.username}</p>
                      <p className="truncate text-xs text-[#7e8cab]">{`${controller?.profile?.coname} - ${controller?.profile?.dvno}`}</p>
                    </div>
                    <Button
                      danger
                      type="text"
                      icon={<LogoutOutlined />}
                      loading={controller.logoutMutation.isPending}
                      onClick={() => controller.logoutMutation.mutate()}
                    >
                      Logout
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-b border-[#e7edf7] bg-[#fbfcff] px-4 py-3 sm:px-6">
              <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
                <NavTabs
                  tabs={controller.state.openTabs}
                  activeTabId={controller.state.activeTabId}
                  onChange={controller.actions.setActiveTab}
                  onClose={controller.actions.closeTab}
                  getTabHref={(tab, index) => toHashRoute(tab, index + 1, controller.isFormOpen ? 'form' : tab.viewMode)}
                />

                <Space wrap size={10}>
                  <Tooltip title="Buat data baru">
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      disabled={!controller.canCreate}
                      onClick={controller.startCreateRecord}
                    >
                      New Record
                    </Button>
                  </Tooltip>

                  <Tooltip title="Refresh data aktif">
                    <Button icon={<ReloadOutlined />} onClick={controller.refreshCurrentData}>
                      Refresh
                    </Button>
                  </Tooltip>


                  {controller.isFormOpen ? (
                    <Button icon={<EditOutlined />} onClick={controller.cancelFormEdit}>
                      Back to list
                    </Button>
                  ) : null}
                </Space>
              </div>
            </div>

            <div className="px-4 py-4 sm:px-6 sm:py-5">
              <Card
                bordered={false}
                className="workspace-content-shell !rounded-[24px] !border !border-[#e8eef8] !shadow-none"
                bodyStyle={{ padding: 0 }}
              >
                <div className="flex items-center justify-between gap-3 border-b border-[#e8eef8] px-5 py-4">
                  <div>
                    <Text className="!text-xs !font-semibold !uppercase !tracking-[0.14em] !text-[#8a96b3]">Workspace View</Text>
                    <Title level={5} className="!mb-0 !mt-1 !text-[#223d73]">
                      {controller.showFormPage
                        ? controller.activeFormIntent === 'create'
                          ? 'Create Record'
                          : 'Edit Record'
                        : controller.activeTab?.viewMode === 'cards'
                          ? 'Card Explorer'
                          : 'Data Grid'}
                    </Title>
                  </div>

                  {controller.activePermsQuery.isLoading ? <Tag color="processing">Checking permissions</Tag> : null}
                  {controller.activePermsQuery.isError ? <Tag color="error">Permissions unavailable</Tag> : null}
                </div>

                <div className="min-h-[520px] bg-white">
                  {controller.activeActionQuery.isLoading ? (
                    <div className="flex min-h-[280px] items-center justify-center">
                      <Space align="center" size={12}>
                        <Spin />
                        <Text className="!text-[#7383a4]">Memuat action view...</Text>
                      </Space>
                    </div>
                  ) : null}

                  {controller.activeActionQuery.isError ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description="Action gagal dimuat dari server."
                      className="py-16"
                    />
                  ) : null}

                  {!controller.activeTab ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_DEFAULT}
                      description="Pilih menu di sidebar untuk membuka dynamic tab view."
                      className="py-16"
                    />
                  ) : null}

                  {controller.activeRecordsQuery.isLoading ? (
                    <div className="flex items-center gap-3 px-5 py-4 text-sm text-[#7383a4]">
                      <Spin size="small" />
                      <span>Memuat data model dari backend...</span>
                    </div>
                  ) : null}

                  {controller.activeRecordsQuery.isError ? (
                    <div className="px-5 py-4 text-sm text-[#d14343]">Data model gagal dimuat dari endpoint ws/rest.</div>
                  ) : null}

                  {controller.activeRecordFetchQuery.isLoading && controller.isFormOpen ? (
                    <div className="px-5 py-3 text-xs text-[#7383a4]">Memuat detail record...</div>
                  ) : null}

                  {!controller.showFormPage && !controller.filteredRecords.length && controller.activeTab ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description="Belum ada data yang tampil untuk modul ini."
                      className="py-16"
                    />
                  ) : null}

                  {!controller.showFormPage && controller.activeTab?.viewMode !== 'cards' && controller.filteredRecords.length ? (
                    <ListView
                      records={controller.filteredRecords}
                      visibleColumns={controller.visibleColumns}
                      selectedRecordId={String(controller.selectedRecord?.id ?? '')}
                      canEdit={controller.canEdit}
                      canRemove={controller.canRemove}
                      renderCell={controller.renderCell}
                      onEditRecord={controller.startEditForRecord}
                      onDeleteRecord={(record) => {
                        controller.selectRecord(record)
                        controller.deleteRecordMutation.mutate()
                      }}
                      onSelectRecord={controller.selectRecord}
                    />
                  ) : null}

                  {!controller.showFormPage && controller.activeTab?.viewMode === 'cards' && controller.filteredRecords.length ? (
                    <CardView
                      records={controller.filteredRecords}
                      visibleColumns={controller.visibleColumns}
                      selectedRecordId={String(controller.selectedRecord?.id ?? '')}
                      canEdit={controller.canEdit}
                      getRecordTitle={controller.getRecordTitle}
                      onEditRecord={controller.startEditForRecord}
                      onSelectRecord={controller.selectRecord}
                    />
                  ) : null}

                  {controller.showFormPage ? (
                    <FormView
                      formIntent={controller.activeFormIntent}
                      formRecord={controller.activeFormRecord ?? {}}
                      isSaving={controller.saveRecordMutation.isPending}
                      saveErrorMessage={controller.saveErrorMessage}
                      getRecordTitle={controller.getRecordTitle}
                      onSave={() => controller.saveRecordMutation.mutate()}
                      onCancel={controller.cancelFormEdit}
                      onUpdateField={controller.updateDraftField}
                    />
                  ) : null}
                </div>
              </Card>
            </div>
          </Card>
        </section>
      </div>
    </main>
  )
}
