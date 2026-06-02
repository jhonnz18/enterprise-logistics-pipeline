# High-Performance Enterprise Logistics Pipeline & Orchestration

An end-to-end, production-grade Data Engineering pipeline designed to ingest, govern, and process concurrent fleet telemetric events. The architecture features an in-memory transformation layer, immutable containerization, automated Windows Server orchestration with exponential back-off resilience, and real-time localized BI reporting.

## 📈 System Architecture & Data Flow

```text
[ Concurrent API Streams ] ──(ThreadPool)──> [ Ingest Engine ]
                                                   │
                                            (Polars Cleansing)
                                                   │
                                                   ▼
[ PowerShell Orchestrator ] ──(Monitors)──> [ Docker Runtime ] ──> [ JSON Logs / Parquet Storage ]
                                                                                  │
                                                                           (Looker Studio BI)