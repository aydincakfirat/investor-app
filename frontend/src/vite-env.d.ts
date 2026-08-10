/// <reference types="vite/client" />

// CSS Modules type declarations
// Vite handles CSS modules at runtime; this tells TypeScript to accept them.
declare module '*.module.css' {
  const classes: Record<string, string>
  export default classes
}

declare module '*.module.scss' {
  const classes: Record<string, string>
  export default classes
}
