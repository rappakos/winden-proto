from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Process():
    active_day:str = None
    active_winde:str = None
    active_wf:str = None