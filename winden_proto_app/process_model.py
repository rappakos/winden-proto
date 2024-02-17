from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum

class WindeStatus(Enum):
    GARAGE = 0
    AUFGEBAUT = 1
    ABGEBAUT = 2



@dataclass_json
@dataclass
class Process():
    active_day:str = None
    pilot_list:bool = None
    active_winde:str = None
    winde_status:WindeStatus = WindeStatus.GARAGE
    active_wf:str = None
