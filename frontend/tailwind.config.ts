import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "dt-bg": "#0a0e17",
        "dt-surface": "#111827",
        "dt-surface-alt": "#1a2332",
        "dt-border": "#1e293b",
        "dt-text": "#e2e8f0",
        "dt-text-muted": "#94a3b8",
        "dt-accent": "#3b82f6",
        "dt-accent-dim": "#1e40af",
        "dt-healthy": "#22c55e",
        "dt-degraded": "#f59e0b",
        "dt-failing": "#ef4444",
        "dt-critical": "#dc2626",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "SF Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "ping-slow": "ping 2s cubic-bezier(0, 0, 0.2, 1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
