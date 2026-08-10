import type { ReactNode } from 'react'
import Card from '@/components/ui/Card'
import StatusBadge from '@/components/ui/StatusBadge'
import { useHealth, useReadiness } from '@/hooks/useHealth'
import styles from './StatusPage.module.css'

export default function StatusPage() {
  const { data: health, isLoading: hLoading, isError: hError } = useHealth()
  const { data: ready, isLoading: rLoading, isError: rError } = useReadiness()

  return (
    <div className={styles.wrapper}>
      <Card title="Backend API">
        <dl className={styles.dl}>
          <Row label="Status">
            {hLoading ? (
              <StatusBadge status="loading" />
            ) : hError ? (
              <StatusBadge status="unhealthy" />
            ) : (
              <StatusBadge status={health!.status} />
            )}
          </Row>
          <Row label="Version">
            <code className={styles.mono}>{health?.version ?? '—'}</code>
          </Row>
          <Row label="Environment">
            <code className={styles.mono}>{health?.environment ?? '—'}</code>
          </Row>
          <Row label="Uptime">
            <code className={styles.mono}>
              {health ? formatUptime(health.uptime_seconds) : '—'}
            </code>
          </Row>
        </dl>
      </Card>

      <Card title="Database">
        <dl className={styles.dl}>
          <Row label="Readiness">
            {rLoading ? (
              <StatusBadge status="loading" />
            ) : rError ? (
              <StatusBadge status="unavailable" />
            ) : (
              <StatusBadge status={ready!.database} />
            )}
          </Row>
          <Row label="Connection">
            <code className={styles.mono}>{ready?.status ?? '—'}</code>
          </Row>
        </dl>
      </Card>

      <Card title="Platform Components" className={styles.wide}>
        <table className={styles.table} aria-label="Platform component status">
          <thead>
            <tr>
              <th>Component</th>
              <th>Phase</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <ComponentRow name="Backend API"        phase="1" status="healthy" />
            <ComponentRow name="Frontend"           phase="1" status="healthy" />
            <ComponentRow name="PostgreSQL"         phase="1" status="healthy" />
            <ComponentRow name="n8n Orchestrator"   phase="1" status="healthy" />
            <ComponentRow name="Market Data"        phase="2" status="not_ready" />
            <ComponentRow name="Technical Analysis" phase="3" status="not_ready" />
            <ComponentRow name="Fundamentals"       phase="4" status="not_ready" />
            <ComponentRow name="News Engine"        phase="5" status="not_ready" />
            <ComponentRow name="Signal Engine"      phase="6" status="not_ready" />
            <ComponentRow name="n8n Workflows"      phase="7" status="not_ready" />
            <ComponentRow name="AI Analyst"         phase="8" status="not_ready" />
            <ComponentRow name="Email / Alerts"     phase="9" status="not_ready" />
            <ComponentRow name="Portfolio"          phase="10" status="not_ready" />
            <ComponentRow name="Backtesting"        phase="11" status="not_ready" />
          </tbody>
        </table>
      </Card>
    </div>
  )
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className={styles.row}>
      <dt className={styles.dt}>{label}</dt>
      <dd className={styles.dd}>{children}</dd>
    </div>
  )
}

function ComponentRow({ name, phase, status }: { name: string; phase: string; status: string }) {
  return (
    <tr>
      <td>{name}</td>
      <td><code className={styles.mono}>Phase {phase}</code></td>
      <td>
        <StatusBadge
          status={status as Parameters<typeof StatusBadge>[0]['status']}
          label={status === 'healthy' ? 'Active' : 'Pending'}
        />
      </td>
    </tr>
  )
}

function formatUptime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
}
