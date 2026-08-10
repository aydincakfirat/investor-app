import clsx from 'clsx'
import styles from './StatusBadge.module.css'

type Status = 'healthy' | 'degraded' | 'unhealthy' | 'ready' | 'not_ready' | 'ok' | 'unavailable' | 'loading'

interface Props {
  status: Status
  label?: string
}

const STATUS_MAP: Record<Status, { label: string; variant: string }> = {
  healthy:    { label: 'Healthy',     variant: 'success' },
  ready:      { label: 'Ready',       variant: 'success' },
  ok:         { label: 'OK',          variant: 'success' },
  degraded:   { label: 'Degraded',    variant: 'warning' },
  unhealthy:  { label: 'Unhealthy',   variant: 'danger' },
  not_ready:  { label: 'Not Ready',   variant: 'danger' },
  unavailable:{ label: 'Unavailable', variant: 'danger' },
  loading:    { label: 'Checking…',   variant: 'muted' },
}

export default function StatusBadge({ status, label }: Props) {
  const { label: defaultLabel, variant } = STATUS_MAP[status] ?? STATUS_MAP.loading
  return (
    <span
      className={clsx(styles.badge, styles[variant])}
      aria-label={`Status: ${label ?? defaultLabel}`}
    >
      <span className={styles.dot} aria-hidden="true" />
      {label ?? defaultLabel}
    </span>
  )
}
