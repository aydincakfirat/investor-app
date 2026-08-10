import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Briefcase,
  Star,
  Bell,
  BarChart2,
  Activity,
} from 'lucide-react'
import styles from './Sidebar.module.css'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/markets', label: 'Markets', icon: TrendingUp },
  { to: '/portfolio', label: 'Portfolio', icon: Briefcase },
  { to: '/watchlist', label: 'Watchlist', icon: Star },
  { to: '/signals', label: 'Signals', icon: BarChart2 },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/status', label: 'System Status', icon: Activity },
]

export default function Sidebar() {
  return (
    <aside className={styles.sidebar} aria-label="Main navigation">
      <div className={styles.logo}>
        <svg width="24" height="24" viewBox="0 0 32 32" fill="none" aria-hidden="true">
          <rect width="32" height="32" rx="6" fill="#0f172a"/>
          <polyline points="4,24 10,16 16,20 22,10 28,14"
            stroke="#22d3ee" strokeWidth="2.5"
            strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          <circle cx="28" cy="14" r="2" fill="#22d3ee"/>
        </svg>
        <span className={styles.logoText}>InvestAI</span>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [styles.navItem, isActive ? styles.active : ''].join(' ')
            }
          >
            <Icon size={18} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className={styles.footer}>
        <span className={styles.version}>Phase 1 · MVP</span>
      </div>
    </aside>
  )
}
