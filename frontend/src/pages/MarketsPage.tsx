import { useEffect, useMemo, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import Card from '@/components/ui/Card'
import { marketApi } from '@/services/api'
import type { MarketCandle, MarketQuote } from '@/types/api'

import styles from './MarketsPage.module.css'

const PERIODS = [
  { label: '1 month', value: '1mo' },
  { label: '3 months', value: '3mo' },
  { label: '6 months', value: '6mo' },
  { label: '1 year', value: '1y' },
] as const

export default function MarketsPage() {
  const [markets, setMarkets] = useState<MarketQuote[]>([])
  const [selectedKey, setSelectedKey] = useState('sp500')
  const [period, setPeriod] = useState('1mo')
  const [candles, setCandles] = useState<MarketCandle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void marketApi.getOverview().then((response) => {
      setMarkets(response.markets)
      if (!response.markets.some((market) => market.key === selectedKey)) {
        setSelectedKey(response.markets[0]?.key ?? '')
      }
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Market data could not be loaded.')
    })
  }, [selectedKey])

  const selectedMarket = markets.find((market) => market.key === selectedKey)

  useEffect(() => {
    if (!selectedMarket) return

    setLoading(true)
    setError(null)
    void marketApi.getHistory(selectedMarket.symbol, period).then((response) => {
      setCandles(response.candles)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Market history could not be loaded.')
      setCandles([])
    }).finally(() => setLoading(false))
  }, [period, selectedMarket])

  const chartData = useMemo(() => candles
    .filter((candle) => candle.close !== null)
    .map((candle) => ({
      date: new Date(candle.timestamp).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      }),
      close: candle.close,
    })), [candles])

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Phase 2 · Market Data</p>
          <h2>Markets</h2>
          <p className={styles.subtitle}>Explore live quotes and persisted price history.</p>
        </div>
        <div className={styles.controls}>
          <label>
            <span>Instrument</span>
            <select value={selectedKey} onChange={(event) => setSelectedKey(event.target.value)}>
              {markets.map((market) => <option key={market.key} value={market.key}>{market.name}</option>)}
            </select>
          </label>
          <label>
            <span>Period</span>
            <select value={period} onChange={(event) => setPeriod(event.target.value)}>
              {PERIODS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <Card title={selectedMarket?.name ?? 'Market history'} className={styles.chartCard}>
        {loading ? <div className={styles.empty}>Loading history...</div> : chartData.length === 0 ? (
          <div className={styles.empty}>No historical data available for this instrument.</div>
        ) : (
          <div className={styles.chart}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 12, right: 20, left: 0, bottom: 4 }}>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis domain={['auto', 'auto']} tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} width={68} />
                <Tooltip contentStyle={{ background: '#17243a', border: '1px solid #334155', borderRadius: 6 }} />
                <Line type="monotone" dataKey="close" stroke="#22d3ee" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>
    </div>
  )
}
