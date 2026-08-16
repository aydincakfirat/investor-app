/**

* API response types shared across the application.
* These match the Pydantic schemas on the backend.
  */

export interface HealthResponse {
status: 'healthy' | 'degraded' | 'unhealthy'
version: string
environment: string
uptime_seconds: number
}

export interface ReadinessResponse {
status: 'ready' | 'not_ready'
database: 'ok' | 'unavailable'
}

export interface ApiError {
detail: string
status_code?: number
}

export interface MarketQuote {
key: string
name: string
symbol: string
region: string
price: number | null
currency: string | null
change: number | null
change_percent: number | null
timestamp: string | null
}

export interface MarketOverview {
markets: MarketQuote[]
}

export interface MarketCandle {
timestamp: string
open: number | null
high: number | null
low: number | null
close: number | null
volume: number | null
}

export interface MarketHistory {
symbol: string
interval: string
range: string
candles: MarketCandle[]
}
