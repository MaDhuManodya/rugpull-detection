# Early Rug Pull Detection in Blockchain Using Graph Neural Networks and Temporal Learning

> **Undergraduate Research Project** | Python 3.12 · PyTorch · FastAPI · Next.js

A production-quality research prototype implementing a multimodal, graph-attentional, temporally aware, and explainable rug pull detection system for Ethereum and BNB Smart Chain.

---

## Architecture Overview

```
On-chain (ETH/BSC) + Smart Contract + OSINT
              │
    ┌─────────▼──────────┐
    │  Data Collection   │  Etherscan · BscScan · Web3 · DeFiLlama
    └─────────┬──────────┘
              │  (enforced BEFORE Project Midpoint — no leakage)
    ┌─────────▼──────────┐
    │ Feature Engineering │  On-chain · Contract · Graph · Temporal
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │ Multimodal Fusion  │  Late fusion of all 4 modalities
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │   GATv2  + TGN     │  Spatial attention + Temporal memory
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │ Binary Classifier  │  P(rug pull) + lead-time metric
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │  SHAP + GNNExplain │  Feature + structural attribution
    └────────────────────┘
```

---

## Research Paper

**Title**: Early Rug Pull Detection in Blockchain Using Graph Neural Networks and Temporal Learning  
**Contribution**: First framework to combine GATv2 + TGN + full 4-modality fusion + dual explainability for rug pull detection.

### Six Research Gaps Addressed
| Gap | Solution |
|---|---|
| No combined graph + temporal model | GATv2 (spatial) + TGN (temporal) together |
| Limited multimodal fusion | All 4 modalities: on-chain + contract + graph + OSINT |
| Weak explainability | SHAP (features) + GNNExplainer (structure) |
| Static graph learning | Continuous-time dynamic graph via TGN |
| No dynamic temporal learning | TGN memory (GRU) across full token lifespan |
| Insufficient early prediction | Lead time metric reported explicitly |

---

## Project Structure

```
rugpull-detection/
├── backend/          # FastAPI + ML pipeline
├── frontend/         # Next.js dashboard
├── datasets/         # Data and labelling
├── experiments/      # MLflow experiment tracking
├── trained_models/   # Saved model weights
├── docs/             # Architecture diagrams
├── scripts/          # CLI tools
└── docker-compose.yml
```

---

## Quick Start

### Prerequisites
- Docker ≥ 24 + Docker Compose v2
- Python 3.12 (for local dev)
- Node.js 20 (for frontend)

### 1. Clone & Configure
```bash
git clone <repo>
cd rugpull-detection
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Launch All Services
```bash
docker-compose up --build
```

### 3. Access
| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| Celery Monitor | http://localhost:5555 |
| PgAdmin | http://localhost:5050 |

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI + asyncpg + SQLAlchemy 2.0 |
| Database | PostgreSQL 16 + Redis 7 |
| Task Queue | Celery 5 |
| Graph ML | PyTorch + PyTorch Geometric |
| Baselines | XGBoost, Random Forest, scikit-learn |
| Explainability | SHAP + GNNExplainer (PyG) |
| Blockchain | Web3.py, Etherscan API, BscScan API, Alchemy |
| Frontend | Next.js 14 + TailwindCSS + React Flow |
| Containers | Docker + Docker Compose |

---

## Development Phases

| Phase | Description | Status |
|---|---|---|
| 1 | Project Setup | ✅ Complete |
| 2 | Database Models | 🔄 Next |
| 3 | Blockchain Collectors | ⏳ Pending |
| 4 | Feature Engineering | ⏳ Pending |
| 5 | Graph Construction | ⏳ Pending |
| 6 | ML Training Pipeline | ⏳ Pending |
| 7 | Explainability | ⏳ Pending |
| 8 | REST API | ⏳ Pending |
| 9 | Frontend Dashboard | ⏳ Pending |
| 10 | Evaluation Scripts | ⏳ Pending |

---

## License
MIT — Academic Research Use
