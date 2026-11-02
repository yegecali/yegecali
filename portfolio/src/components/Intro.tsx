import { Sparkles } from 'lucide-react'
import { usePortfolio } from '../context/PortfolioContext'
import FloatingAccent from './motion/FloatingAccent'

export default function Intro() {
  const { t } = usePortfolio()
  return (
    <section className="intro" data-aos="portfolio-up">
      <p className="eyebrow"><span />{t.hello}</p>
      <h2>{t.title}<br /><span>{t.title2}</span><FloatingAccent className="intro-spark"><Sparkles size={31} /></FloatingAccent></h2>
      <p>{t.intro}</p>
    </section>
  )
}
