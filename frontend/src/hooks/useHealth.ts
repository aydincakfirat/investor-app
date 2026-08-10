import { useQuery } from '@tanstack/react-query'
import { healthApi } from '@/services/api'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: healthApi.getHealth,
    refetchInterval: 60_000,
  })
}

export function useReadiness() {
  return useQuery({
    queryKey: ['readiness'],
    queryFn: healthApi.getReadiness,
    refetchInterval: 30_000,
    retry: false,
  })
}
