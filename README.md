
# 🚀 FastAPI Project

A project built with **FastAPI**, featuring testing support, Docker containerization, and local deployment via Kubernetes on Docker Desktop.

---

## ✨ Key Features

- ✅ Modern and high-performance API with **FastAPI**
- 🧪 Automated testing with **pytest**
- 📊 Code coverage with **pytest-cov**
- 🐳 Containerization using **Docker**
- ☸️ Orchestration with **Kubernetes**
- ⚖️ Auto-scaling via **Horizontal Pod Autoscaler**
- 🌐 External access through **Ingress Controller**
- 🔧 Environment configuration using **ConfigMap**
- 🔁 Full deployment with a **PowerShell** script

---

## 📦 Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/) or `venv` and `pip`
- Docker
- Kubernetes (Docker Desktop with K8s enabled)
- PowerShell (to run the apply-k8s.ps1 script)

---

## 🔧 Local Setup & Execution


### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the local server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ✅ Running Tests

```bash
pytest
```

### 📊 Viewing Test Coverage

```bash
pytest --cov=app
```

Install the coverage plugin with:

```bash
pip install pytest-cov
```

---

## 🐳 Docker

### 1. Build the image

```bash
docker build -t fastapi-local:1.0 .
```

### 2. Run the container

```bash
docker run -p 8000:8000 fastapi-local:1.0
```

### 3. Access the application

[http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☸️ Kubernetes (via Docker Desktop)

### 1. Enable Kubernetes in Docker Desktop

- Go to **Settings > Kubernetes** and check **Enable Kubernetes**

### 2. Run the deployment script

```powershell
.\apply-k8s.ps1
```

This script automatically applies all Kubernetes manifests:

- `deployment.yaml`: Defines pods and containers
- `service.yaml`: Exposes the service internally
- `configmap.yaml`: Declares environment variables
- `ingress.yaml`: Enables external access via domain/path
- `hpa.yaml`: Auto-scales pods based on CPU usage
- `apply-k8s.ps1`: Automates the application of all YAML files

### 3. Check if pods are running

```bash
kubectl get pods
```

### 4. Port-forward (for local testing without ingress)

```bash
kubectl port-forward svc/fastapi-service 8000:8000
```

Access: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 K8s Files Structure

- `deployment.yaml`: Defines replicas, resources, probes, and container image
- `service.yaml`: Creates a `ClusterIP` service
- `configmap.yaml`: Centralizes app configurations
- `ingress.yaml`: Applies HTTP routing rules for exposure
- `hpa.yaml`: Automatically scales pods based on load
- `apply-k8s.ps1`: Automates the application of all manifests

---
---
---

# 📦 Logistics API – Route Overview

This API powers a logistics platform used to manage and monitor shipments of general goods via vessels. The system supports contract management, cargo tracking, vessel availability, and client information retrieval.

---

## 🌐 Base URL

By default:
```
http://localhost:8000
```

Interactive Swagger docs:
```
http://localhost:8000/docs
```

---

## 🧭 API Features & Routes Overview

### 1. 📃 **Contracts** – `/contracts`

- **Create a contract**
  - `POST /contracts/`
- **Retrieve contract by ID**
  - `GET /contracts/{contract_id}`
- **List all contracts (paginated)**
  - `GET /contracts/`
- **Search by client**
  - `GET /contracts/search/by-client/{client_id}`
- **Search by status**
  - `GET /contracts/search/by-status?status=ACTIVE`
- **Filter active contracts within a date range**
  - `GET /contracts/search/active?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- **Update/Delete contracts**
  - `PUT` / `DELETE /contracts/{contract_id}`

🔍 **Clients can:**
- View contract details (client name, cargo type, destination, price)

---

### 2. 📦 **Cargo** – `/cargo`

- **Create cargo**
  - `POST /cargo/`
- **Get cargo by ID**
  - `GET /cargo/{cargo_id}`
- **Get cargo with tracking**
  - `GET /cargo/{cargo_id}/with-tracking`
- **List all cargoes (paginated)**
  - `GET /cargo/`
- **Update/Delete cargo**
  - `PUT` / `DELETE /cargo/{cargo_id}`
- **Filter by contract, status, or destination**
  - `GET /cargo/search/by-contract/{contract_id}`
  - `GET /cargo/search/by-status?status=IN_TRANSIT`
  - `GET /cargo/search/by-destination?destination=Lisbon`

🔍 **Clients can:**
- Check cargo status (pending, in transit, delivered)

---

### 3. ⛴ **Vessels** – `/vessels`

- **Register a vessel**
  - `POST /vessels/`
- **Retrieve vessel by ID**
  - `GET /vessels/{vessel_id}`
- **List all vessels (paginated)**
  - `GET /vessels/`
- **Search vessels**
  - By name: `GET /vessels/search/by-name?name=VesselX`
  - By status: `GET /vessels/search/by-status?status=ACTIVE`
  - By location: `GET /vessels/search/by-location?location=Porto`
  - Available vessels: `GET /vessels/search/available?min_capacity=5000`

🔍 **Clients can:**
- Retrieve vessel details (name, capacity, current location)

---

### 4. 📍 **Tracking** – `/trackings`

- **Create a tracking record**
  - `POST /trackings/`
- **Get tracking record by ID**
  - `GET /trackings/{tracking_id}`
- **List all tracking records (paginated)**
  - `GET /trackings/`
- **Get all trackings for a cargo or vessel**
  - `GET /trackings/by-cargo/{cargo_id}`
  - `GET /trackings/by-vessel/{vessel_id}`
- **Get latest tracking or full history**
  - `GET /trackings/latest/{cargo_id}`
  - `GET /trackings/history/{cargo_id}`
- **Filter by tracking status**
  - `GET /trackings/status/{status}`

🔍 **Clients can:**
- Access full tracking history (locations where cargo has been)

---

## 👥 **Clients** – `/clients`

- **Create a client**
  - `POST /clients/`
- **Get client by ID**
  - `GET /clients/{client_id}`
- **List all clients (paginated)**
  - `GET /clients/`
- **Search clients by name**
  - `GET /clients/search/?name=John`

---

## ✅ Summary of What Clients Can Do

| Feature                     | Endpoint Example                                  |
|----------------------------|----------------------------------------------------|
| View contract details       | `GET /contracts/{contract_id}`                    |
| Check cargo status          | `GET /cargo/{cargo_id}`                           |
| Get vessel info             | `GET /vessels/{vessel_id}`                        |
| View tracking history       | `GET /trackings/history/{cargo_id}`              |

---

## 📝 Notes

- All endpoints use JSON format.
- Use Swagger UI at `/docs` to explore and test endpoints.
- Ensure proper ID references across contracts, cargoes, and vessels.

---
# 📑 SQLAlchemy Indexes Overview

This document explains the database indexes configured in your SQLAlchemy models to optimize queries and enforce constraints efficiently.

---

## ⚙️ Why Indexes Matter

Indexes are critical for:
- Improving **lookup and filter performance**
- Enabling **efficient pagination**
- Supporting **foreign key joins**
- Optimizing **frequent query paths**

---

## 📦 Cargo Model

**Table**: `cargo`

```python
Index("ix_cargo_status", "status")
Index("ix_cargo_destination", "destination")
```

✅ Optimizes:
- Queries that filter by cargo status (e.g., IN_TRANSIT, DELIVERED)
- Searches by destination in user-facing filters

---

## 👥 Client Model

**Table**: `client`

```python
CheckConstraint("credit_limit >= 0", name="ck_client_credit_limit_non_negative")
```

✅ Ensures:
- Business logic rule: credit limit must be 0 or positive.

🔍 Note: No additional indexes explicitly declared — relies on primary key and unique constraint on `tax_id`.

---

## 📃 Contract Model

**Table**: `contract`

```python
Index("ix_contract_client_id", "client_id")
```

✅ Optimizes:
- Joins between contracts and clients
- Lookups by client (e.g., fetch all contracts for a given client)

---

## 📍 Tracking Model

**Table**: `tracking`

```python
Index("ix_tracking_cargo_id", "cargo_id")
Index("ix_tracking_location", "location")
Index("ix_tracking_status", "status")
```

✅ Optimizes:
- Lookups of all tracking entries for a cargo
- Geolocation filters by location
- Real-time status-based queries (e.g., LOADING, DELAYED)

---

## 🧾 TrackingHistory Model

**Table**: `tracking_history`

```python
Index("ix_tracking_history_cargo_id", "cargo_id")
Index("ix_tracking_history_tracking_id", "tracking_id")
```

✅ Optimizes:
- History lookups by cargo or tracking ID

---

## ⛴ Vessel Model

**Table**: `vessel`

```python
Index("ix_vessel_name", "name")
Index("ix_vessel_current_location", "current_location")
```

✅ Optimizes:
- Searches by vessel name (used in exact-match endpoints)
- Filters by vessel current location (used for location-based tracking)

---

## 🧱 BaseModel

Every model inherits common indexed columns via `BaseModel`:

- `id`: Primary key (indexed automatically)
- `created_at`, `updated_at`: Timestamp tracking for sorting/filtering

---

## ✅ Summary

| Table             | Indexed Columns                                 |
|------------------|--------------------------------------------------|
| `cargo`           | `status`, `destination`                         |
| `client`          | `tax_id` (unique), `credit_limit` (check)      |
| `contract`        | `client_id`                                     |
| `tracking`        | `cargo_id`, `location`, `status`                |
| `tracking_history`| `cargo_id`, `tracking_id`                       |
| `vessel`          | `name`, `current_location`                      |

Use these indexes to ensure your API stays fast, even with large volumes of data.

---

# 🚀 Async API Design & Schemas Overview

This project uses **FastAPI** with a fully asynchronous architecture, leveraging `async` and `await` for high performance under concurrent workloads such as cargo tracking, contract management, and vessel logistics.

---

## ⚙️ Why Async?

FastAPI natively supports asynchronous endpoints using Python's `asyncio`, which allows:
- 🔁 Non-blocking I/O for database queries
- 🚀 Faster response under high concurrency
- ⚡ Efficient use of server resources (especially with PostgreSQL & async DB drivers)

---

## 🧬 Schema Design Overview

Schemas are built using **Pydantic**, offering:
- Input validation
- Output formatting
- Type-safe data serialization
- Reuse across create/update/response patterns

---

## 📐 Base Schemas

### `BaseSchema`
- Root class for all input models
- Enables config: `from_attributes`, `arbitrary_types_allowed`

### `BaseResponseSchema`
- Adds common fields: `id`, `created_at`, `updated_at`

### `PaginatedResponse[T]`
Generic paginated structure for listing endpoints:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

---

## 📦 Cargo Schemas

- `CargoCreate`, `CargoUpdate`: for creation and partial updates
- `CargoResponse`: combines base + metadata
- Validation:
  - Status must be a valid `CargoStatus`
  - Arrival date must be after departure

---

## 👥 Client Schemas

- `ClientCreate`, `ClientUpdate`, `ClientResponse`
- Strong validation for:
  - Email
  - Tax ID format (9 digits)
  - Payment terms (e.g., "30 days")

---

## 📃 Contract Schemas

- `ContractCreate`, `ContractUpdate`, `ContractResponse`
- Validates:
  - Contract period
  - Currency codes (e.g., USD, EUR)
  - Price range sanity check

---

## 📍 Tracking Schemas

- `TrackingCreate`, `TrackingUpdate`, `TrackingResponse`
- `TrackingHistoryResponse` for audit log
- Validation:
  - Enum constraints on `TrackingStatus`
  - Timestamps default to `datetime.utcnow`

---

## ⛴ Vessel Schemas

- `VesselCreate`, `VesselUpdate`, `VesselResponse`
- Validates:
  - Name and location cannot be blank
  - Year built is reasonable (not in distant future)
  - Status must match `VesselStatus` enum

---

## 🧪 Example of Validation

```python
@field_validator("status")
def validate_status(cls, v):
    if v not in [s.value for s in CargoStatus]:
        raise ValueError("Invalid cargo status")
    return v
```

This ensures consistent API behavior and clear error messaging for clients.

---

## ✅ Summary

| Entity     | Create Schema     | Update Schema     | Response Schema        |
|------------|-------------------|-------------------|------------------------|
| Cargo      | `CargoCreate`     | `CargoUpdate`     | `CargoResponse`        |
| Client     | `ClientCreate`    | `ClientUpdate`    | `ClientResponse`       |
| Contract   | `ContractCreate`  | `ContractUpdate`  | `ContractResponse`     |
| Tracking   | `TrackingCreate`  | `TrackingUpdate`  | `TrackingResponse`     |
| Vessel     | `VesselCreate`    | `VesselUpdate`    | `VesselResponse`       |

This structure promotes scalability, testability, and maintainability in asynchronous systems.

