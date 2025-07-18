"""permanent project data"""
#cspell: disable
from typing import Literal
from models.components import Component as Equip, Specs, Tech
from models.consumption import ElectricityBill as Bill
from models.econometrics import Cost, Currency as Curr
from models.geometry import Orientation
from models.inventory import Building
from models.photovoltaic import PvInput
from libs.repository import forehouse

type Subject = Literal['project','consumptions','components']

#gen
PANELS:int=28
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'SFV Consistorial Agarrobo ',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.367006, -71.673254),
            name='Consistorial Algarrobo',
            address='Av. Peñablanca 250, 2710767 Algarrobo',
            city='Algarrobo'),
    },
    'consumptions':{
        'cost_increment':5.8,
        'client_id':'181-3',
        'measurer_id':'190045687/704223',
        'contract_id':'BT2PP',
        'consumption':[
            Bill("21-12-2023","20-01-2024",2_617,326_816,Curr.CLP,('BT','_2','PP')),
            Bill("20-01-2024","22-02-2024",2_745,341_469,Curr.CLP,('BT','_2','PP')),
            Bill("24-02-2024","24-03-2024",1_588,199_468,Curr.CLP,('BT','_2','PP')),
            Bill("24-03-2024","24-04-2024",1_588,199_468,Curr.CLP,('BT','_2','PP')),
            Bill("24-04-2024","24-05-2024",2_041,297_678,Curr.CLP,('BT','_2','PP')),
            Bill("24-05-2024","24-06-2024",2_041,297_678,Curr.CLP,('BT','_2','PP')),
            Bill("24-06-2024","24-07-2024",1_810,274_111,Curr.CLP,('BT','_2','PP')),
            Bill("24-07-2024","24-08-2024",1_810,274_111,Curr.CLP,('BT','_2','PP')),
            Bill("24-08-2024","24-09-2024",1_891,307_903,Curr.CLP,('BT','_2','PP')),
            Bill("24-09-2024","24-10-2024",1_891,307_903,Curr.CLP,('BT','_2','PP')),
        ]
    },
    'components':{
        'generator':(
            forehouse['CS 655W'],# equipment
            PvInput(
                description='FV 655W mod A',
                quantity=28,
                orientation=Orientation(20,0-(90-40)),
                ),
        ),
        'install':(
            'instalación',
            forehouse['Inverter']['CS 15kW H'],# inverter
            forehouse['Medidor']['FR 3F'],# lectura
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
            forehouse['Monitor']['VC 700'],
            forehouse['Regulator']['VT 45A']
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