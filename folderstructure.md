Project root folder
web-vuln-scanner/
│
├── docker-compose.yml
├── README.md
├── .env
│
├── api-gateway/
├── crawler-service/
├── attack-surface-service/
├── payload-service/
├── detection-service/
├── report-service/
│
└── shared/
    ├── models/
    ├── utils/
    └── config/


Modules

api-gateway/
│
├── app.py
├── routes.py
├── requirements.txt
├── Dockerfile
└── config.py

crawler-service/
│
├── app.py
├── crawler/
│   ├── crawler_engine.py
│   ├── link_extractor.py
│   ├── form_parser.py
│   └── session_manager.py
│
├── services/
│   └── crawl_service.py
│
├── requirements.txt
└── Dockerfile


attack-surface-service/
│
├── app.py
├── surface/
│   ├── attack_object.py
│   ├── parameter_mapper.py
│   └── context_identifier.py
│
├── services/
│   └── surface_service.py
│
├── requirements.txt
└── Dockerfile


payload-service/
│
├── app.py
├── payload_engine/
│   ├── payload_loader.py
│   ├── context_detector.py
│   ├── injector.py
│   └── payload_selector.py
│
├── payloads/
│   ├── xss.txt
│   ├── sqli.txt
│   ├── cmd.txt
│   └── traversal.txt
│
├── requirements.txt
└── Dockerfile

detection-service/
│
├── app.py
├── detection/
│   ├── response_diff.py
│   ├── evidence_engine.py
│   ├── confidence_score.py
│   └── vulnerability_mapper.py
│
├── services/
│   └── detection_service.py
│
├── requirements.txt
└── Dockerfile

report-service/
│
├── app.py
├── report/
│   ├── report_builder.py
│   ├── template_engine.py
│   └── severity_formatter.py
│
├── templates/
│   └── report_template.html
│
├── requirements.txt
└── Dockerfile

shared/
│
├── models/
│   ├── scan_request.py
│   ├── attack_object.py
│   └── vulnerability.py
│
├── utils/
│   ├── http_client.py
│   ├── logger.py
│   └── helpers.py
│
└── config/
    └── settings.py






     You (Person A)

    crawler-service

    attack-surface-service

    partial API gateway logic

👨‍💻 Friend (Person B)

    payload-service

    detection-service

    report-service
