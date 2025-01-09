from typing import Any, Dict


def parse_and_convert(result: Any) -> Dict:
    return result.model_dump()
