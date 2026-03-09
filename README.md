# Digital Twin of the Internet

A real-time digital simulation of the internet's infrastructure and health. This platform visualizes the global internet as a living 3D system and predicts outages or anomalies using AI-powered analysis.

![Architecture](https://img.shields.io/badge/architecture-distributed-blue)
![Backend](https://img.shields.io/badge/backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/frontend-Next.js%20%2B%20Three.js-purple)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  Next.js + React + Three.js + TypeScript + Tailwind          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ 3D Globe │ │ Health   │ │ Incident │ │ AI Prediction│   │
│  │ View     │ │ Panel    │ │ Panel    │ │ Panel        │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│                      │ WebSocket + REST                      │
└──────────────────────┼──────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────┐
│                   Backend (FastAPI)                           │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐  │
│  │ Network        │ │ Latency        │ │ Incident        │  │
│  │ Monitor        │ │ Simulator      │ │ Detector        │  │
│  └────────────────┘ └────────────────┘ └─────────────────┘  │
│  ┌────────────────┐                                          │
│  │ AI Predictor   │ ← Anomaly detection + Root cause        │
│  └────────────────┘                                          │
│                      │                                       │
└──────────────────────┼──────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────┐
│               Simulation Engine                              │
│  ┌────────────────┐ ┌────────────────────────────────────┐  │
│  │ Topology       │ │ Traffic Engine                     │  │
│  │ Generator      │ │ (diurnal, incidents, cascading)    │  │
│  └────────────────┘ └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 3D Interactive Globe
- Rotating earth with infrastructure nodes
- Zoom into network regions
- Clickable nodes with detail panels
- Animated traffic routes as glowing arcs
- Live health indicators with color-coded status

### Infrastructure Simulation
- 250 globally distributed nodes (data centers, cloud regions, backbones, ISPs, satellites, IX points)
- 2000+ traffic routes with realistic latency modeling
- Diurnal traffic patterns and congestion simulation
- Incident injection with cascading failure propagation
- Automatic recovery cycles

### AI Prediction Engine
- Statistical anomaly detection using z-score analysis
- Latency cascade prediction
- Congestion hotspot detection
- Cascading failure risk assessment
- AI-generated root cause analysis

### Dashboard
- Global system health score with breakdown
- Active incidents panel with severity levels
- AI predictions with confidence scores
- Health timeline visualization
- Node detail inspection

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14, React 18, Three.js, TypeScript, Tailwind CSS |
| 3D Rendering | @react-three/fiber, @react-three/drei |
| State Management | Zustand |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| AI/ML | NumPy, scikit-learn |
| Communication | WebSocket (real-time), REST API |

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
cd ..
python -m backend.main
```

The API server starts at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard opens at `http://localhost:3000`.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/snapshot` | Full network snapshot |
| GET | `/api/nodes` | All infrastructure nodes |
| GET | `/api/nodes/{id}` | Single node details |
| GET | `/api/nodes/{id}/analysis` | AI root cause analysis |
| GET | `/api/routes` | Traffic routes |
| GET | `/api/incidents` | Active incidents |
| GET | `/api/predictions` | AI predictions |
| GET | `/api/health` | System health score |
| GET | `/api/heatmap` | Latency heatmap grid |
| GET | `/api/history` | Historical health data |
| WS | `/ws` | Real-time WebSocket feed |

## Node Types

| Type | Description | Count |
|------|-------------|-------|
| Cloud Region | AWS, GCP, Azure regions | 20 |
| Data Center | Equinix, CyrusOne, Digital Realty facilities | 20 |
| Backbone | Tier-1 transit providers (Telia, Lumen, GTT) | 20 |
| ISP | Consumer/enterprise ISPs globally | 20 |
| IX Point | Internet exchange points (DE-CIX, AMS-IX, LINX) | 15 |
| Satellite | LEO/GEO satellite gateways (Starlink, OneWeb) | 10 |

## Node Status

- **Healthy** — Soft green glow, normal metrics
- **Degraded** — Pulsing orange, elevated latency or loss
- **Failing** — Flashing red, critical metric thresholds exceeded
- **Offline** — Grey, complete loss of connectivity

## License

MIT
