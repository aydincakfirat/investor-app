import { useEffect, useMemo, useState } from 'react'

import Card from '@/components/ui/Card'
import { marketApi } from '@/services/api'
import type { MarketQuote } from '@/types/api'

import styles from './DashboardPage.module.css'

const REGIONS = ['Turkey', 'United States', 'Europe'] as const

export default function DashboardPage() {
  const [markets, setMarkets] = useState<MarketQuote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMarkets = async () => {
    try {
      setError(null)

      const response = await marketApi.getOverview()
      setMarkets(response.markets)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Market data could not be loaded.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadMarkets()

    const interval = window.setInterval(() => {
      void loadMarkets()
    }, 60_000)

    return () => {
      window.clearInterval(interval)
    }
  }, [])

  const marketsByRegion = useMemo(() => {
    return REGIONS.map((region) => ({
      region,
      markets: markets.filter((market) => market.region === region),
    }))
  }, [markets])

  return (
    <div className={styles.grid}>
      <div className={styles.banner}>
        <div>
          <h2 className={styles.bannerTitle}>
            Market Intelligence Dashboard
          </h2>

          <p className={styles.bannerSub}>
            Real-time market overview powered by Yahoo Finance.
          </p>
        </div>

        <button
          type="button"
          className={styles.refreshButton}
          onClick={() => void loadMarkets()}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className={styles.error}>
          <strong>Market data unavailable</strong>
          <span>{error}</span>
        </div>
      )}

      {marketsByRegion.map(({ region, markets: regionMarkets }) => (
        <Card
          key={region}
          title={region}
          className={styles.card}
        >
          {loading && markets.length === 0 ? (
            <div className={styles.loading}>
              Loading market data...
            </div>
          ) : regionMarkets.length === 0 ? (
            <div className={styles.loading}>
              No market data available.
            </div>
          ) : (
            <MarketList markets={regionMarkets} />
          )}
        </Card>
      ))}

      <Card
        title="Investment Ideas"
        className={styles.cardWide}
      >
        <p className={styles.placeholder}>
          AI-generated long-term, swing, and short-term opportunities will
          appear here in a later phase.
        </p>
      </Card>
    </div>
  )
}

function MarketList({ markets }: { markets: MarketQuote[] }) {
  return (
    <ul className={styles.marketList}>
      {markets.map((market) => (
        <li
          key={market.key}
          className={styles.marketRow}
        >
          <div className={styles.marketName}>
            <span>{market.name}</span>
            <small>{market.symbol}</small>
          </div>

          <div className={styles.marketValue}>
            <span className={styles.price}>
              {formatPrice(market.price, market.currency)}
            </span>

            <ChangeValue
              change={market.change}
              changePercent={market.change_percent}
            />
          </div>
        </li>
      ))}
    </ul>
  )
}

function ChangeValue({
  change,
  changePercent,
}: {
  change: number | null
  changePercent: number | null
}) {
  if (changePercent === null) {
    return <span className={styles.changeNeutral}>—</span>
  }

  const positive = changePercent > 0
  const negative = changePercent < 0

  const className = positive
    ? styles.changePositive
    : negative
      ? styles.changeNegative
      : styles.changeNeutral

  const sign = positive ? '+' : ''

  return (
    <span className={className}>
      {sign}
      {changePercent.toFixed(2)}%
      {change !== null && (
        <span className={styles.changeAbsolute}>
          {' '}
          ({sign}
          {formatNumber(change)})
        </span>
      )}
    </span>
  )
}

function formatPrice(
  price: number | null,
  currency: string | null,
): string {
  if (price === null) {
    return '—'
  }

  const currencyMap: Record<string, string> = {
    TRY: 'tr-TR',
    USD: 'en-US',
    EUR: 'de-DE',
    GBP: 'en-GB',
  }

  const locale = currency
    ? currencyMap[currency] ?? 'en-US'
    : 'en-US'

  try {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: price < 10 ? 4 : 2,
    }).format(price)
  } catch {
    return price.toFixed(2)
  }
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}
