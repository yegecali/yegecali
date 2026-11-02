import { Activity, Cloud, Code2, Database, Github, Layers3, Linkedin, ShieldCheck, Terminal } from 'lucide-react'
import type { LucideIcon, LucideProps } from 'lucide-react'
import type { IconName } from '../../types/portfolio'

const icons: Record<IconName, LucideIcon> = {
  activity: Activity,
  cloud: Cloud,
  code: Code2,
  database: Database,
  github: Github,
  layers: Layers3,
  linkedin: Linkedin,
  shield: ShieldCheck,
  terminal: Terminal,
}

type IconProps = LucideProps & { name: IconName }

export default function Icon({ name, ...props }: IconProps) {
  const Component = icons[name] || Code2
  return <Component {...props} />
}
