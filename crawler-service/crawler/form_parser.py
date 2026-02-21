from bs4 import BeautifulSoup

def extract_forms(html: str):
    soup = BeautifulSoup(html, "lxml")
    forms_data = []

    for form in soup.find_all("form"):
        action = form.get("action")
        method = form.get("method", "GET").upper()

        inputs = []
        for input_tag in form.find_all("input"):
            name = input_tag.get("name")
            if name:
                inputs.append(name)

        forms_data.append({
            "action": action,
            "method": method,
            "inputs": inputs
        })

    return forms_data