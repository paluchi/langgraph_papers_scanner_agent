from langchain.output_parsers import CommaSeparatedListOutputParser


class NewlineListOutputParser(CommaSeparatedListOutputParser):
    def parse(self, text: str):
        return [item.strip() for item in text.strip().split("\\n")]
