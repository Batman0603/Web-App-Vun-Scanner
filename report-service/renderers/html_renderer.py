from jinja2 import Environment, FileSystemLoader

class HTMLRenderer:
    @staticmethod
    def render(report: dict) -> str:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("report.html")
        return template.render(report=report)