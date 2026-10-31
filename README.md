# Kyzentra AI

Multi-service workspace powering the Kyzentra AI platform.

## Services Architecture

| Service | Technology | Port | Directory | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Next.js 16 + React 19 | `3000` | [frontend/](file:///d:/kyzentra/frontend) | Builds and starts production server (`npm run build && npm run start`). Runs `npm install` if `node_modules` is absent. |
| **Backend** | FastAPI + Uvicorn | `8000` | [backend/](file:///d:/kyzentra/backend) | Uses `venv` (creates if missing, installs `requirements.txt`). Runs with `--reload`. |
| **Kie** | FastAPI + Uvicorn | `8001` | [Kie/](file:///d:/kyzentra/Kie) | Uses `.venv` (creates if missing, installs `requirements.txt`). Runs with `--reload`. |
| **Kie-2** | FastAPI + Uvicorn | `8002` | [kie-2/](file:///d:/kyzentra/kie-2) | Uses `.venv` (creates if missing, installs `requirements.txt`). Runs with `--reload`. |

---

## How to Run All Services

You have three convenient ways to launch all four services in separate terminal windows:

### Option 1: Windows Batch File (Recommended for Double-Click or CMD)
Simply double-click [run_services.bat](file:///d:/kyzentra/run_services.bat) in File Explorer, or execute in terminal:
```cmd
.\run_services.bat
```

### Option 2: PowerShell
Run the PowerShell launcher script:
```powershell
.\run_services.ps1
```

### Option 3: Python Runner
Run using Python:
```bash
python run_services.py
```

---

## Running an Individual Service

You can also run any specific service in isolation by passing its name:

| Service | Batch Command | PowerShell Command |
| :--- | :--- | :--- |
| **Frontend** | `.\run_services.bat frontend` | `.\run_services.ps1 -Service frontend` |
| **Backend** | `.\run_services.bat backend` | `.\run_services.ps1 -Service backend` |
| **Kie** | `.\run_services.bat kie` | `.\run_services.ps1 -Service kie` |
| **Kie-2** | `.\run_services.bat kie-2` | `.\run_services.ps1 -Service kie-2` |

---

## Stop Services

To quickly stop all running services and free ports `3000`, `8000`, `8001`, and `8002`:

- **Batch**: `.\stop_services.bat`
- **PowerShell**: `.\stop_services.ps1`