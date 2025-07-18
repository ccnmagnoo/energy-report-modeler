"""permanent project data"""
#cspell: disable
from typing import Literal
from models.components import Component as Equip, Specs, Tech
from models.consumption import ElectricityBill as Bill
from models.econometrics import Cost, Currency as Curr
from models.geometry import Orientation
from models.inventory import Building
from models.photovoltaic import PvInput
from libs.repository import forehouse,panelRepo

type Subject = Literal['project','consumptions','components']

#gen
PANELS:int=80
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'FV H. San José',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.314975, -71.414803),
            name='H. San José',
            address='Juan Verdaguer 122',
            city='Casablanca'),
    },
    'consumptions':{
        'cost_increment':4.7,
        'client_id':'250837-0',
        'measurer_id':'10033891',
        'contract_id':'AT-4.3 ',
        'consumption':[
            Bill("11-04-2024","13-05-2024",81_480,9_550805,Curr.CLP,('AT','_43','NA')),
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W mod',
                quantity=80,
                orientation=Orientation(20,43),
                ),
        ),
        'install':(
            'instalación',
            forehouse['Inverter']['CS 50kW H'],# inverter
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
                cost_per_unit=Cost(55_000),
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
                    taller='3 Hrs',
                    manual='6 u. impreso',
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
                )
        ),
        'overloads':{
            'gastos_gral':30,
            'utilidad':20
        }
    }
}