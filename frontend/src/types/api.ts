/**
 * API response types shared across the application.
 * These match the Pydantic schemas on the backend.
 * Phase 1: health/status only. Additional types are added in later phases.
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
