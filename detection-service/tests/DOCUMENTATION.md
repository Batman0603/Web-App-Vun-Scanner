# Detection Service Tests

This directory contains test resources, fixtures, and documentation for the Detection Service tests.

## Contents

*   `sample_payload_response.json`: A sample JSON file representing the expected output structure from the detection logic, specifically illustrating a SQL injection (sqli) test case.

## Swagger / OpenAPI Documentation

The following OpenAPI definition describes the schema for the detection response object found in `sample_payload_response.json`.

```yaml
components:
  schemas:
    DetectionResponse:
      type: object
      properties:
        baseline_length:
          type: integer
          description: The content length of the baseline response (without payload).
          example: 528
        payload_type:
          type: string
          description: The category of the payload (e.g., sqli, xss).
          example: "sqli"
        results:
          type: array
          description: List of results for individual payloads.
          items:
            type: object
            properties:
              payload:
                type: string
                description: The specific payload string injected.
                example: "SQL_TEST_123"
              length:
                type: integer
                description: The content length of the response when the payload was used.
                example: 600
```
