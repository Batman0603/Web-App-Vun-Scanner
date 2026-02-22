from weasyprint import HTML

class PDFRenderer:
    @staticmethod
    def render(html_content: str) -> bytes:
        return HTML(string=html_content).write_pdf()