/**

* Centralised API client.
* VITE_API_BASE_URL defaults to empty string so that Vite's dev proxy
* or Kubernetes Ingress handles the routing transparently.
  */

import axios from 'axios'

import type {
HealthResponse,
MarketHistory,
MarketOverview,
ReadinessResponse,
} from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const apiClient = axios.create({
baseURL: BASE_URL,
timeout: 15_000,
headers: {
'Content-Type': 'application/json',
},
})

// ── Response interceptor: normalise errors ────────────────────────────────────

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ?? err.message ?? 'Unknown error'

    return Promise.reject(new Error(message))
  },
)

// ── Health API ─────────────────────────────────────────────────────────────────

export const healthApi = {
  getHealth: () =>
    apiClient.get<HealthResponse>('/api/health').then((r) => r.data),

  getReadiness: () =>
    apiClient.get<ReadinessResponse>('/api/ready').then((r) => r.data),
}

// ── Market API ─────────────────────────────────────────────────────────────────

export const marketApi = {
  getOverview: () =>
    apiClient
      .get<MarketOverview>('/api/markets/overview')
      .then((r) => r.data),

  getHistory: (
    symbol: string,
    range = '1mo',
    interval = '1d',
  ) =>
    apiClient
      .get<MarketHistory>(`/api/markets/${encodeURIComponent(symbol)}/history`, {
        params: {
          range,
          interval,
        },
      })
      .then((r) => r.data),
}
