<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6a00ff,100:ff00cc&height=220&section=header&text=WAVS&fontSize=70&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Web%20Application%20Vulnerability%20Scanner&descAlignY=60"/>

<br>

```text
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░░▒▓█▓▒▒▓█▓▒░ ░▒▓██████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░ 
 ░▒▓█████████████▓▒░░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██▓▒░  ░▒▓███████▓▒░  
```

A distributed, microservices-based web vulnerability scanner designed to automate the discovery and analysis of security flaws in web applications. This tool orchestrates a multi-stage pipeline—from crawling to report generation—to identify potential injection vulnerabilities like XSS and SQLi.

## 🚀 Architecture Overview

The application is composed of several specialized Python services that communicate over HTTP, orchestrated by an API Gateway:

1.  **API Gateway (`:8000`)**: The central entry point. Orchestrates the workflow by calling services in sequence.
2.  **Crawler Service (`:8001`)**: Recursively discovers links and extracts HTML forms from a target domain.
3.  **Attack Surface Service (`:8002`)**: Analyzes crawled data to map out attack objects (URLs and parameters).
4.  **Payload Service (`:8003`)**: Conducts context-aware injection attacks using specialized payload lists.
5.  **Detection Service (`:8004`)**: Analyzes response differentials and evidence to confirm vulnerabilities and assign confidence scores.
6.  **Report Service (`:8005`)**: Aggregates findings and generates summaries in JSON or PDF formats.
7.  **Shared Library**: A common internal package used by all services for logging, models, and HTTP utilities.

## 🛠️ Prerequisites

- Docker
- Docker Compose

## 🏃 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd web-vuln-scanner
    ```

2.  **Configure environment:**
    Create a `.env` file in the root directory (if not already present) to manage service configurations.

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    The API Gateway will be available at `http://localhost:8000`.

## �️ WAVS CLI

Install the CLI from the repository root:
```bash
pip install .
```

Then run the tool with:
```bash
WAVS run
```

The CLI will prompt for a target URL and crawl depth, then execute the full pipeline through the API Gateway.

## �📡 API Usage

### Start a New Scan
To trigger the full scanning pipeline, send a request to the API Gateway:

**Endpoint:** `POST /scan`

**Request Body:**
```json
{
  "url": "http://testphp.vulnweb.com",
  "depth": 2
}
```

**Workflow sequence:**
`Crawl` ➡️ `Analyze Surface` ➡️ `Bulk Inject` ➡️ `Detect` ➡️ `Generate Report`

### Health Checks
Each service provides a `/health` endpoint to verify its status:
- Gateway: `http://localhost:8000/health`
- Crawler: `http://localhost:8001/health`
- (and so on for ports 8002-8005)

## 📂 Project Structure

```text
web-vuln-scanner/
├── api-gateway/            # Workflow orchestration logic
├── crawler-service/        # Scrapy/BeautifulSoup discovery engine
├── attack-surface-service/ # Parameter and endpoint mapper
├── payload-service/        # Injection engine and payload files
├── detection-service/      # Heuristic and diff-based analysis
├── report-service/         # PDF/JSON report generation
├── shared/                 # Common utilities and Pydantic models
└── docker-compose.yml      # Multi-container orchestration
```

## ⚖️ Disclaimer
This tool is for educational and authorized security testing purposes only. Never run this scanner against targets you do not have explicit permission to test.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.