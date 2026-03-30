import { Tabs } from 'antd'
import { X } from 'lucide-react'
import type { MouseEvent, ReactNode } from 'react'
import type { AppTab } from '@/store/app-store'

type NavTabsProps = {
  tabs: AppTab[]
  activeTabId: string | null
  onChange: (tabId: string) => void
  onClose: (tabId: string) => void
  getTabHref?: (tab: AppTab, index: number) => string
}

function TabLabel(props: {
  tab: AppTab
  href?: string
  onSelect: () => void
  onClose: () => void
}) {
  const { tab, href, onSelect, onClose } = props

  const handleSelect = (event: MouseEvent<HTMLAnchorElement | HTMLButtonElement>) => {
    event.preventDefault()
    onSelect()

    if (href) {
      window.location.hash = href.startsWith('#') ? href.slice(1) : href
    }
  }

  const handleClose = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    event.stopPropagation()
    onClose()
  }

  const content: ReactNode = (
    <>
      <span className=" text-[#8a1df1]" title={tab.title}>
        {tab.title}
      </span>
      <button
        type="button"
        onClick={handleClose}
        className="rounded p-0.5 text-slate-400 transition-colors hover:bg-slate-200 hover:text-slate-700"
        aria-label={`Tutup tab ${tab.title}`}
      >
        <X className="h-4 w-4" />
      </button>
    </>
  )

  if (href) {
    return (
      <a href={href} onClick={handleSelect} className="flex min-w-0 items-center gap-2">
        {content}
      </a>
    )
  }

  return (
    <button type="button" onClick={handleSelect} className="flex min-w-0 items-center gap-2 text-left">
      {content}
    </button>
  )
}

export function NavTabs({ tabs, activeTabId, onChange, onClose, getTabHref }: NavTabsProps) {
  if (!tabs.length) {
    return (
      <div className="border-b border-indigo-100 bg-white px-4 py-2 text-xs text-slate-500">
        Belum ada tab terbuka. Pilih menu untuk membuka tab.
      </div>
    )
  }

  return (
    <div className="border-b border-indigo-100 bg-white px-2 pt-1">
      <Tabs
        type="card"
        size="small"
        activeKey={activeTabId ?? tabs[0]?.id}
        onChange={onChange}
        className="workspace-nav-tabs"
        items={tabs.map((tab, index) => ({
          key: tab.id,
          label: (
            <TabLabel
              tab={tab}
              href={getTabHref?.(tab, index)}
              onSelect={() => onChange(tab.id)}
              onClose={() => onClose(tab.id)}
            />
          ),
          children: null,
        }))}
      />
    </div>
  )
}
