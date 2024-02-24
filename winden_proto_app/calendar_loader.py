# calendar_loader.py
import os
import json
import requests
from abc import ABC, abstractmethod
from typing import List
from bs4 import BeautifulSoup
from datetime import date

from .models import CalPilot

# for any importer
class CalendarLoader(ABC):
    @abstractmethod
    def load_pilots() -> List[CalPilot]:
        pass



class GscSuedheideLoader(CalendarLoader):

    def filter_reg(self, f):
        today, SET_OKMAYBE= date.today().isoformat(), set(["+","~"])
        entry = f['tage'][0]
        #
        return entry['datum']==today and not SET_OKMAYBE.isdisjoint([entry['frueh'],entry['spaet']] )

    def get_cal_pilot(self, f) -> CalPilot:
        p = CalPilot()
        p.calendar_id = f['fahrer']['id']
        p.name = f['fahrer']['name']
        return p 

    def load_pilots(self) -> List[CalPilot]:
        url = os.environ.get('CALENDAR_URL',None)
        if url:
            #print(url)
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, "html.parser")

            script_data = soup.find('script',attrs={'src': None}) # data not in the table
            table_data_str=script_data.get_text().replace("var jsonPlanStr='",'').strip()[:-2] # remove  "var ...='" & "';"
            table_data_json = json.loads(table_data_str)

        return [self.get_cal_pilot(f) for f in table_data_json['bereitschaften'] if self.filter_reg(f) ]    

