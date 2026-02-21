"""
Extracts HTML form details from a web page.

This module uses BeautifulSoup to parse HTML and find all `<form>` tags,
extracting key information like the action, method, and input field names.
"""
from bs4 import BeautifulSoup

def extract_forms(html: str):
    """
    Parses HTML to find and return details of all forms.

    Args:
        html (str): The HTML content of the page as a string.

    Returns:
        list: A list of dictionaries, where each dictionary represents a form
              and contains its 'action', 'method', and a list of 'inputs'.
    """
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