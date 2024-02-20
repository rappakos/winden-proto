# models.py
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum

PILOT_STATUS = {
    'G': 'Gast',
    'NG': 'Nord-Gast',
    'M': 'Mitglied',
    'WIA': 'WindenFiA',
    'W': 'Windenfahrer',
    'WF': 'Windenfahrer',
    'EWF': 'EWF',
}


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
    active_ewf:str = None

@dataclass_json
@dataclass 
class Winde():
    winde_id:str = None
    name: str = None
    active:bool = False
    baujahr:int = None

@dataclass_json
@dataclass 
class Pilot():
    id:str = None
    name:str = None
    status:str = None
    zugkraft:int = 0
    calendar_id: str= None
    verein: str = None
    schlepp_count: int = 0