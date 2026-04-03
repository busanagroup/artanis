import { IconBrandGithub, IconBrandLinkedin, IconBrandMedium, IconBrandX } from '@tabler/icons-react'

import { Logo } from '@/ui/elements'

interface Social {
  url: string
  icon: React.ReactElement
}

const social: Social[] = [
  { url: 'https://github.com/busanagroup/', icon: <IconBrandGithub /> },
  { url: 'https://www.linkedin.com/company/busanagroup/', icon: <IconBrandLinkedin /> },
  { url: 'https://twitter.com/busanagroup', icon: <IconBrandX /> },
  { url: 'https://dev.to/busanagroup', icon: <IconBrandMedium /> },
]

export default function Footer() {
  return (
    <footer>
      <div className="border-busana-500/50 border-t px-4 py-2 sm:px-6 md:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <a href="https://busanagroup.com">
            <Logo logo="busana" color="busana" size="lg" />
          </a>
          <div className="divide-busana-500/50 flex h-8 items-center justify-end divide-x">
            {social.map((item, i) => (
              <a key={i} href={item.url} className="px-2 first:pl-0 last:pr-0">
                <div className="text-primary-400 hover:text-busana-500 h-6 w-6 transition-colors duration-200">
                  {item.icon}
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
