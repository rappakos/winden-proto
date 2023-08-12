# winden-proto
A prototype app to administering tow winch operation for paragliders

# Models

## Winde

### Kerndaten

* ID
* Name
* Baujahr
* Status 

### Aufbau-Protokoll

List

### Abbau-Protokoll

List

## Pilot

* Name: Text
* Gewicht: 
* Status: List EWF, WF, WIA, MG (default?), NVB, G, INACTIV
* Verein: Text
* Enthaftungserklärung: Bool


## Schlepp

* Datum
* Winde
* Windenfahrer
* EWF
* Pilot
* Status: List started (default), finished, canceled
* SchleppStart
* StatusDate


# Running the app on Windows

* Install requirements, eg `py -m pip install -r .\requirements.txt`
* Start application, eg `py app.py`
* Open url in browser, eg `http://localhost:3978`, check the [config.py](./config.py) for the actual port.

# Installing and running the app on Android

## Installing

* Install F-Droid
* From F-Driod, install Termux
* Start Termux
* In current prompt `~`: `pkg update` 
* In current prompt `~`: `pkg install git`
* In current prompt `~`: `pkg install python`
* pkg i python-numpy
* pkg i python-pandas
* pip install xlsxwriter
* In current prompt `~`: `pkg install libexpat` ?
* In current prompt `~`: `mkdir github`
* In current prompt `~`: `cd github`
* Once in `~/github`: `git clone https://github.com/rappakos/winden-proto.git`
* From `~/github`: `cd winden-proto`
* In `~/github/winden-proto`: `python -m pip install -r .\requirements.txt`

## Running the app

* Start Termux
* In current prompt `~`: `cd github/winden-proto`
* In `~/github/winden-proto`: `python app.py`
* In a browser: go to `http://localhost:3978`


# Storyboard

![Windenaufbau](./storyboard/windenaufbau.PNG)

![Flugkladde](./storyboard/flugkladde.PNG)

![Windenabbau](./storyboard/windenabbau.PNG)

![Datensatzpflege](./storyboard/datensatzpflege.PNG)


# Ideas 

Use [aiohttp demos](https://github.com/aio-libs/aiohttp-demos/tree/master/demos/polls)
