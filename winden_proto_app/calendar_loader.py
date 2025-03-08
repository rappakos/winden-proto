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

class DummyCalendarLoader(CalendarLoader):

    def load_pilots(self) -> List[CalPilot]:
        res = []
        for pi in [
            ['Akos','f_26'],
            ['Orsi','f_27'],
            ['Sabine','f_17'],
            ['MichaelH', 'f_7'],
            ['Kai F','f_153']
        ]:
            p = CalPilot()
            p.calendar_id=pi[1]
            p.name=pi[0]
            res.append(p)

        return res


class GscSuedheideLoader(CalendarLoader):

    def filter_reg(self, f):
        # 'Flugwetter', 'Schleppbetrieb', 'Gastpiloten
        #if f['fahrer']['id'] in ['f_1', 'f_133','f_106']:
        if f['fahrer']['name'] in ['Flugwetter', 'Schleppbetrieb', 'Gastpiloten']:
            return False

        today, SET_OKMAYBE= date.today().isoformat(), set(["+","~"])
        entry = f['tage'][0]
        #
        return entry['datum']==today and not SET_OKMAYBE.isdisjoint([entry['frueh'],entry['spaet']] )

    def get_cal_pilot(self, f) -> CalPilot:
        #print(f)
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
            table_data_str=script_data.get_text().split(';')[0].replace("var jsonPlanStr='",'').strip()[:-1]
            table_data_json = json.loads(table_data_str)

        return [self.get_cal_pilot(f) for f in table_data_json['bereitschaften'] if self.filter_reg(f) ]    


class TestLoader(CalendarLoader):

     def filter_reg(self, f):
        if f['fahrer']['name'] in ['Flugwetter', 'Schleppbetrieb', 'Gastpiloten']:
            return False
        
        return True

     def load_pilots(self):
        url =  os.environ.get('CALENDAR_URL',None)
        if url:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, "html.parser")
            #print(soup)
            script_data = soup.find('script',attrs={'src': None})
            table_data_str=script_data.get_text().split(';')[0].replace("var jsonPlanStr='",'').strip()[:-1]
            print(table_data_str[:10],' ..... ', table_data_str[-10:])
            table_data_json = json.loads(table_data_str)
            print([[f['fahrer']['name'], f['tage'][0]] for f in table_data_json['bereitschaften'] if self.filter_reg(f)])
        else:
            raise ValueError("URL for the calendar is undefined")

        return []
     

if __name__=='__main__':
    from dotenv import load_dotenv
    load_dotenv('../.env')

    #loader = TestLoader()
    loader = GscSuedheideLoader()

    x = loader.load_pilots()
    print(x)