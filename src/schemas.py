
from dataclasses import dataclass
from enum import Enum
from typing import List


class EmailType(str, Enum):
    EXAMPLE_TYPE = "example-type"

@dataclass
class EmailProperties:
    subject: str
    sections: List[str]
