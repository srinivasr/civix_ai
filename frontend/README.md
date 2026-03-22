# 🎨 Civix AI - Frontend

The presentation layer of **Civix AI**. Built with speed, reactivity, and a premium aesthetic in mind. It uses a modern glassmorphic design system and integrates interactive network structures to represent the Knowledge Graph natively in the browser.

---

## 🛠 Tech Stack

- **Framework**: React 19 + Vite
- **Styling**: Vanilla CSS (Dark Theme + Glassmorphism)
- **Graph Visualization**: `vis-network` & `vis-data` (Louvain Community clustering & PageRank)
- **Tooling**: ESLint, Node.js

---

## 📂 Project Structure

```text
frontend/
 ├── public/             # Static Assets
 ├── src/
 │   ├── components/     # Reusable UI Blocks
 │   │   ├── Dashboard.jsx         # Main Metrics & Risk Overview
 │   │   ├── AskPanel.jsx          # Chat UI for Natural Language Cypher Queries
 │   │   ├── UploadPanel.jsx       # CSV & PDF File Dropzone with OCR status
 │   │   ├── GraphAnalyticsPanel.jsx # Threat Intelligence Network mapping
 │   │   └── AboutPanel.jsx        # System Architecture diagrams
 │   ├── App.jsx         # Main React Component & Routing
 │   ├── index.css       # Global Styles, Glassmorphic Theming & Animations
 │   └── main.jsx        # React DOM Entry Point
 ├── eslint.config.js    # Modern flat-config ESLint rules
 ├── package.json        # Dependencies and Scripts
 ├── vite.config.js      # Vite Configurations
 └── README.md           # Frontend Documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** (v18.x or later)
- **npm** (v9.x or later)

### 2. Installation

Navigate to the frontend directory and install the necessary dependencies:

```bash
cd frontend
npm install
```

### 3. Running the Development Server

Fire up the Vite server with Hot Module Replacement (HMR) capabilities:

```bash
npm run dev
```

The frontend will be instantly accessible, normally at: `http://localhost:5173`

*(Note: Make sure the FastAPI backend is concurrently running on port 8000 so the frontend can successfully retrieve and display the graph data!)*

---

## 💠 Design Principles

The UI of Civix AI is built around the concept of a **Living Dashboard**:
- **Premium Aesthetics**: Deep, carefully curated custom dark palettes combined with vibrant, purposeful accent colors (e.g., Amber for high-risk zones, Blue for active connections).
- **Glassmorphism Integration**: Floating panels and transparent CSS blurs that bring the interactive Knowledge Graph to the forefront without clutter.
- **Dynamic Interaction**: Utilizes `vis-network` to allow users to physically drag, zoom, and explore node connections within the civic dataset.
- **Real-Time Responsiveness**: Stat cards dynamically calculate progress bars, Resolution Rates, and Active Action-Items fetched directly from the Neo4j backend.

---

## 🔧 Scripts Available

- `npm run dev`: Starts the development server.
- `npm run build`: Bundles the application for production.
- `npm run preview`: Locally previews the production build.
- `npx eslint src/`: Runs the linter to verify code quality.
