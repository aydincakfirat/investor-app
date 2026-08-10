import type { ReactNode } from 'react'
import clsx from 'clsx'
import styles from './Card.module.css'

interface Props {
  title?: string
  children: ReactNode
  className?: string
}

export default function Card({ title, children, className }: Props) {
  return (
    <section className={clsx(styles.card, className)}>
      {title && <h2 className={styles.title}>{title}</h2>}
      <div className={styles.body}>{children}</div>
    </section>
  )
}
