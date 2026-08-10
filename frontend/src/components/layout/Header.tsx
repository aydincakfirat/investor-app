import { useLocation } from 'react-router-dom'
import styles from './Header.module.css'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/markets': 'Markets',
  '/portfolio': 'Portfolio',
  '/watchlist': 'Watchlist',
  '/signals': 'Signals',
  '/alerts': 'Alerts',
  '/status': 'System Status',
}

export default function Header() {
  const { pathname } = useLocation()
  const title = PAGE_TITLES[pathname] ?? 'Investment Intelligence'

  return (
    <header className={styles.header} role="banner">
      <h1 className={styles.title}>{title}</h1>
      <div className={styles.right}>
        <span className={styles.date}>
          {new Date().toLocaleDateString('en-GB', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            year: 'numeric',
          })}
        </span>
      </div>
    </header>
  )
}
