from payload_engine.payload_loader import PayloadLoader

if __name__ == "__main__":
    loader = PayloadLoader()
    payloads = loader.load("sqli")
    print(payloads)