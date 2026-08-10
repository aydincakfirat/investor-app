import { Link } from 'react-router-dom'
import styles from './NotFoundPage.module.css'

export default function NotFoundPage() {
  return (
    <div className={styles.wrapper} role="main">
      <p className={styles.code}>404</p>
      <h1 className={styles.title}>Page not found</h1>
      <p className={styles.sub}>The page you are looking for does not exist yet.</p>
      <Link to="/dashboard" className={styles.link}>Go to Dashboard</Link>
    </div>
  )
}
