# PlagCode - Code Similarity Detection System

PlagCode is a modern, Dockerized web application for detecting code plagiarism and similarity across multiple programming languages using token-based analysis (Jaccard Index).

## 🚀 Features

- **Multi-language Support**: Analyze Python, Java, C++, JavaScript, and more.
- **Real-time Processing**: Upload files and track progress live.
- **Deterministic Analysis**: Reliable similarity scores based on token overlap.
- **Visual Reports**: Interactive heatmaps, relationship graphs, and side-by-side code diffs.
- **Dockerized**: Easy setup and deployment with full isolation.
- **Persistent Storage**: Scan metadata/results stored in Postgres; uploaded files + JSON reports stored in MinIO (S3).

## 📂 Project Structure

```
PlagCode/
├── backend/            # FastAPI Backend (Python)
│   ├── main.py         # API Endpoints & Logic
│   └── uploads/        # Temporary storage for uploaded files
├── frontend/           # React Frontend (Vite + Tailwind CSS)
│   ├── src/            # UI Components & Logic
│   └── vite.config.js  # Build configuration
├── samples/            # Sample code files for testing
├── docker-compose.yml  # Docker orchestration
└── legacy_archive/     # Old project files (preserved)
```

## 🛠️ Prerequisites

- **Docker Desktop** installed and running.

## 🏁 Quick Start

1. **Start the application**:
   ```bash
   docker-compose up -d --build
   ```

2. **Access the interface**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

3. **Optional: access storage UIs**:
   - **MinIO Console**: [http://localhost:9001](http://localhost:9001)
   - **Postgres**: available on `localhost:5432` (credentials are in `.env`)

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

## 🔍 How to Use

1. **Upload**: Drag & drop your source code files (at least 2).
2. **Scan**: Click "Start Scan" to begin analysis.
3. **Review**:
   - Check the **Table** for similarity scores.
   - Use the **Heatmap** to spot clusters of similarity.
   - Click "View" to inspect the **Code Comparison** and see exactly which lines match.

## 🤝 Development

- **Frontend**: Runs on Node 20. Configured in `frontend/`.
- **Backend**: Runs on Python 3.9. Configured in `backend/`.
- **Network**: Services communicate via the `plagcode-net` Docker network.

---

