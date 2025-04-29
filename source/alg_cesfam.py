"""permanent project data"""
#cspell: disable
from typing import Literal
from models.components import Component as Equip, Specs, Tech
from models.consumption import ElectricityBill as Bill
from models.econometrics import Cost, Currency as Curr
from models.geometry import Orientation
from models.inventory import Building
from models.photovoltaic import PvInput
from libs.repository import repoEquipment,panelRepo

type Subject = Literal['project','consumptions','components']

#gen
PANELS:int=17*3+17*2
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'SFV Cesfam Algarrobo ',
        'connection_type':'netbilling', # netbilling|hybrid|ongrid|offgrid
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.366067,-71.668636),
            name='Cesfam Algarrobo',
            address='Calle Carabineros de Chille Nro 2350',
            city='Algarrobo'),
    },
    'consumptions':{
        'cost_increment':7.3,
        'client_id':'181-3',
        'measurer_id':'59483773/LANDIS-ZMD405CT',
        'contract_id':'BT43',
        'consumption':[
            Bill("21-07-2023","22-08-2024",16200,1502597,Curr.CLP,('BT','_43','NA')),
            Bill("22-08-2024","21-11-2023",14200,1317093,Curr.CLP,('BT','_43','NA')),
            Bill("21-11-2023","20-12-2023",13600,1261439,Curr.CLP,('BT','_43','NA')),
            Bill("20-12-2023","19-01-2024",14600,1354192,Curr.CLP,('BT','_43','NA')),
            Bill("19-01-2024","21-02-2024",12800,1187238,Curr.CLP,('BT','_43','NA')),
            Bill("21-02-2024","21-03-2024",15400,1428395,Curr.CLP,('BT','_43','NA')),
            Bill("21-03-2024","23-04-2024",18400,1706656,Curr.CLP,('BT','_43','NA')),
            Bill("23-04-2024","23-05-2024",17000,1557885,Curr.CLP,('BT','_43','NA')),
            Bill("23-05-2024","19-06-2024",21600,2158857,Curr.CLP,('BT','_43','NA')),
            Bill("19-06-2024","22-07-2024",14800,1479216,Curr.CLP,('BT','_43','NA')),
            Bill("22-07-2024","22-08-2024",11800,1179375,Curr.CLP,('BT','_43','NA')),
            Bill("22-08-2024","23-09-2024",10200,1099295,Curr.CLP,('BT','_43','NA')),
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='PV mod.01 655w',
                quantity=17*3,
                orientation=Orientation(5,20),
                ),
            PvInput(
                description='PV mod.02 655w',
                quantity=17*2,
                orientation=Orientation(5,20),
                ),
        ),
        'install':(
            'instalación',
            repoEquipment['Inverter']['CS 50kW H'],# inverter
            repoEquipment['Medidor']['FR 3F'],# lectura
            Equip(
                description='eléctrica interior',
                specification=Specs(
                    category='Obra',
                    brand='conexionado',
                    model='interiores'
                    ),
                cost_per_unit=Cost(225_000),
                quantity=POWER#power kW
            ),
            Equip(
                description='estructura montaje',
                specification=Specs(
                    category='Montaje',
                    montaje='coplanar',
                    ),
                cost_per_unit=Cost(45_000),
                quantity=PANELS#panels
                ),
            ),
        'storage':(#0 hours for not install storage at all
            'almacenamiento',0,'24/5',
            repoEquipment['Monitor']['VC 700'],
            repoEquipment['Regulator']['VT 45A']
        ),

        'accesories':(
            'obras',
            Equip(
                description='Faenas',
                specification=Specs(
                    category='Obra',
                    brand='equipamiento',
                    model='provisorio'),
                cost_per_unit=Cost(18_750),
                quantity=PANELS#panels
                ),
            Equip(
                description='Capacitación',
                specification=Specs(
                    category='Obra',
                    brand='Uso y',
                    model='mantenimiento',
                    taller='1 Hrs',
                    manual='2 u. impreso',
                    ),
                cost_per_unit=Cost(250_000),
                ),
            Equip(
                description='Letrero',
                specification=Specs(
                    category='Obra',
                    brand='pliego',
                    model='estructura',
                    specs_url='#pliegos-técnicos',
                    dim='3.6m x 1.5m',
                    ),
                cost_per_unit=Cost(450_000),
                ),
        ),
        'overloads':{
            'gastos_gral':15,
            'utilidad':10
        }
    }
}