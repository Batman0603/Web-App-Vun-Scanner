# Payload Service Documentation

## 1. Overview
The Payload Service is a core component of the Web App Vulnerability Scanner. It is responsible for identifying injection points in web applications by analyzing HTTP responses and executing targeted payload attacks.

## 2. System Components

### Context Detector
- **Location**: `payload_engine/context_detector.py`
- **Purpose**: Analyzes how a test marker is reflected in the HTTP response to determine the injection context.
- **Supported Contexts**:
  - `json`: Reflected inside a JSON structure.
  - `html`: Reflected in the HTML body.
  - `attribute`: Reflected inside an HTML tag attribute.
  - `js`: Reflected inside a JavaScript string.
  - `unknown`: No specific context detected.

### Injector
- **Location**: `payload_engine/injector.py`
- **Purpose**: Orchestrates the scanning process.
- **Process**:
  1. Validates input parameters.
  2. Sends a baseline request with a canary (marker).
  3. Detects the context using `ContextDetector`.
  4. Selects appropriate payloads using `PayloadSelector`.
  5. Iterates through payloads and records response characteristics.

### Payload Loader
- **Location**: `payload_engine/payload_loader.py`
- **Purpose**: Loads attack payloads from text files located in the `payloads/` directory.

### Payload Selector
- **Location**: `payload_engine/payload_selector.py`
- **Purpose**: Maps the detected context to a specific vulnerability class (e.g., HTML context triggers XSS payloads).

---

## 3. API Reference (Swagger Docs)

The service exposes a single endpoint to trigger scans.

### `POST /inject`

Initiates a vulnerability scan on a target URL parameter.

#### Request

**URL**: `/inject`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Parameters:**

| Name | Type | Required | Description | Example |
|---|---|---|---|---|
| `url` | string | Yes | The target URL to scan. | `http://target.com/page` |
| `parameter` | string | Yes | The query parameter or form field to inject. | `q` |
| `method` | string | No | HTTP method (`GET` or `POST`). Default: `GET`. | `GET` |

#### Response

**Status**: `200 OK`  
**Content-Type**: `application/json`

**Body Schema:**

| Field | Type | Description |
|---|---|---|
| `target` | string | The URL that was scanned. |
| `parameter` | string | The parameter that was tested. |
| `method` | string | The HTTP method used. |
| `context` | string | The detected injection context. |
| `payload_type` | string | The type of payloads selected (e.g., `xss`, `sqli`). |
| `baseline_length` | integer | The content length of the baseline response. |
| `results` | array[object] | A list of results for each payload injected. |

**Result Object Schema:**

| Field | Type | Description |
|---|---|---|
| `payload` | string | The payload string used. |
| `status` | integer | The HTTP status code returned by the target. |
| `length` | integer | The content length of the response. |

#### Example

**Request:**
```json
{
  "url": "http://testphp.vulnweb.com/listproducts.php",
  "parameter": "cat",
  "method": "GET"
}
```

**Response:**
```json
{
  "target": "http://testphp.vulnweb.com/listproducts.php",
  "parameter": "cat",
  "method": "GET",
  "context": "html",
  "payload_type": "xss",
  "baseline_length": 4520,
  "results": [
    {
      "payload": "<script>alert(1)</script>",
      "status": 200,
      "length": 4545
    }
  ]
}
```
