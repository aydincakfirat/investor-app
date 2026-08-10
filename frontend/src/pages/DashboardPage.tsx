import Card from '@/components/ui/Card'
import styles from './DashboardPage.module.css'

/**
 * Phase 1 dashboard — placeholder content.
 * Real market data, signals, and charts are added in Phase 2+.
 */
export default function DashboardPage() {
  return (
    <div className={styles.grid}>
      {/* Coming-soon banner */}
      <div className={styles.banner}>
        <h2 className={styles.bannerTitle}>Market Intelligence Dashboard</h2>
        <p className={styles.bannerSub}>
          Phase 1 foundation is running. Market data, AI analysis, and signals
          will appear here from Phase 2 onwards.
        </p>
      </div>

      {/* Market overview placeholders */}
      <Card title="Turkey" className={styles.card}>
        <PlaceholderMarket items={['BIST 100', 'BIST Banks', 'USD/TRY', 'EUR/TRY', 'Gold', 'Brent', 'TR 10Y']} />
      </Card>

      <Card title="United States" className={styles.card}>
        <PlaceholderMarket items={['S&P 500', 'Nasdaq 100', 'Dow Jones', 'VIX', 'US 10Y', 'DXY', 'Gold']} />
      </Card>

      <Card title="Europe" className={styles.card}>
        <PlaceholderMarket items={['DAX', 'CAC 40', 'FTSE 100', 'Euro Stoxx 50', 'EUR/USD']} />
      </Card>

      <Card title="Investment Ideas" className={styles.cardWide}>
        <p className={styles.placeholder}>
          AI-generated long-term, swing, and short-term opportunities will appear
          here once the signal engine (Phase 6) and AI analyst (Phase 8) are active.
        </p>
      </Card>
    </div>
  )
}

function PlaceholderMarket({ items }: { items: string[] }) {
  return (
    <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {items.map((item) => (
        <li
          key={item}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '0.875rem',
            color: 'var(--color-text-secondary)',
            padding: '0.375rem 0',
            borderBottom: '1px solid var(--color-border)',
          }}
        >
          <span>{item}</span>
          <span style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
            — DEMO DATA —
          </span>
        </li>
      ))}
    </ul>
  )
}
