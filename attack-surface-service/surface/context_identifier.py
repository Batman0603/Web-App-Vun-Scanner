class ContextIdentifier:

    @staticmethod
    def identify_from_url() -> str:
        return "query"

    @staticmethod
    def identify_from_form(form: dict) -> str:
        enctype = form.get("enctype", "")

        if "application/json" in enctype:
            return "json_body"

        if "multipart/form-data" in enctype:
            return "multipart"

        return "form_body"