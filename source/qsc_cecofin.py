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
PANELS:int=35
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'SFV CECOSF Isla Negra ',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.43839824635554, -71.68396380506573),
            name='CECOSF Isla Negra',
            address='Av. Isidoro Dubournais 4100',
            city='Isla Negra, El Quisco'),
    },
    'consumptions':{
        'cost_increment':5.8,
        'client_id':'n-n',
        'measurer_id':'nd/ni',
        'contract_id':'nd',
        'consumption':[
            Bill("20-01-2024","22-02-2024",2_745,341_469,Curr.CLP,('BT','_2','PP')),
            Bill("24-11-2024","24-12-2024",1_891,307_903,Curr.CLP,('BT','_2','PP')),
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W mod A',
                quantity=35,
                orientation=Orientation(30,-24),
                ),
        ),
        'install':(
            'instalación',
            repoEquipment['Inverter']['KH 25kW'],# inverter
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