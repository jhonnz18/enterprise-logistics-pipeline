# High-Density Logistics Operations & Data Governance Control Tower

## Live Interactive Dashboard
https://datastudio.google.com/reporting/92cb0497-f03e-4855-9fcc-d0ead8b957a4

---

## 🚀 Case Study: Architecture & Business Impact (STAR Methodology)

### 📌 Situation
Logistics operators managing high-density distribution networks in major metropolitan areas face critical financial and operational losses due to a complete lack of real-time fleet visibility. Furthermore, decision-making is severely hindered by corrupted IoT telemetry data—such as null coordinates, network duplicates, and structural anomalies—which compromises key performance indicators (KPIs) and operational SLAs.

### Task
To design and implement a robust, production-ready, and fully automated data infrastructure acting as an **Operations Control Tower**. The system was engineered to fulfill two core technical pillars:
1. Process high-velocity, asynchronous geospatial telemetry streams by simulating real-world multi-stop routing schedules across real city avenues.
2. Implement a strict, in-memory **Data Governance & Quality Guard** layer to intercept and purge data anomalies before storage, guaranteeing an analytical dashboard driven by 100% reliable source data.

### Action
I developed a decoupled, high-performance backend architecture composed of the following modular layers:

1. **Real-Time Telemetry Simulator (`src/simulator.py`):** A custom Python engine that integrates with the open-source OSRM (Open Source Routing Machine) API. It decodes complex route geometries via the `polyline` library to simulate continuous vehicle displacement along real geospatial coordinates.
2. **Data Ingestion & Governance Pipeline (`src/pipeline.py`):** A high-throughput data pipeline optimized with **Polars** to execute schema enforcement, vectorized deduplication in memory, and blazingly fast analytical aggregations.
3. **Local Orchestration (`scripts/run_pipeline.ps1`):** An automation script built in **PowerShell** that coordinates execution cycles, setting up process environments smoothly.
4. **Containerization & Portability:** The entire backend infrastructure was isolated into a **Docker** environment to ensure seamless, cross-platform deployment.
5. **Presentation Layer:** A high-density analytical dashboard styled in deep dark-mode using **Looker Studio**, centralizing operational KPIs (Average Route Duration, Total Completed Deliveries, Max Route Peaks) and plotting live active markers over interactive maps.

### Result
* **Uncompromised Data Trust:** Successfully integrated an automated data quality gate that intercepts and purges structural anomalies on the fly, eliminating the risk of reporting skewed analytics to stakeholder boards.
* **In-Memory Efficiency:** Leveraging Polars significantly reduced processing latencies and computational overhead compared to traditional data manipulation frameworks.
* **Strategic Business Value:** Operations teams gain a unified, symmetric command center capable of auditing route bottlenecks, monitoring transit states, and safeguarding fleet distribution workflows under real-world SLA standards.

---

## Tech Stack
* **Language:** Python 3.11+
* **Data Processing:** Polars
* **Geospatial Analytics:** OSRM API & Polyline
* **Automation & Environment:** PowerShell & Docker
* **Data Visualization:** Looker Studio

---

## ⚙️ Installation & Usage Guide

### Prerequisites
* Docker Desktop installed and running
* Python 3.11 installed (for local script execution)

### Quick Local Deployment

1. Clone the repository:
   ```bash
   git clone [https://github.com/jhonnz18/enterprise-logistics-pipeline.git](https://github.com/jhonnz18/enterprise-logistics-pipeline.git)
   cd enterprise-logistics-pipeline