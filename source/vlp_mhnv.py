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

data:dict[Subject,any] = {
    'project':{
        'title':'Sistema ERNC MHNV',
        'connection_type':'hybrid',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.047016, -71.621509),
            name='Edificio C_Porter MHNV',
            address='Calle Condell 1546',
            city='Valparaíso'),
    },
    'consumptions':{
        'cost_increment':5.5,
        'client_id':'642180-6',
        'measurer_id':'10025437',
        'contract_id':'BT-3 PPP',
        'consumption':[
            Bill("04-01-2023","01-02-2023",1051,97_36_1,Curr.CLP,('BT','_3','PPP')),
            Bill("02-02-2023","02-03-2023",1123,104_031,Curr.CLP,('BT','_3','PPP')),
            Bill("03-03-2023","03-04-2023",1157,107_181,Curr.CLP,('BT','_3','PPP')),
            Bill("04-04-2023","04-05-2023",1220,137_911,Curr.CLP,('BT','_3','PPP')),
            Bill("05-05-2023","01-06-2023",1299,146_841,Curr.CLP,('BT','_3','PPP')),
            Bill("02-06-2023","04-07-2023",1549,175_101,Curr.CLP,('BT','_3','PPP')),
            Bill("05-07-2023","02-08-2023",1353,152_946,Curr.CLP,('BT','_3','PPP')),
            Bill("03-08-2023","01-09-2023",1420,160_519,Curr.CLP,('BT','_3','PPP')),
            Bill("02-09-2023","03-10-2023",1283,145_033,Curr.CLP,('BT','_3','PPP')),
            Bill("04-10-2023","03-11-2023",1275,144_128,Curr.CLP,('BT','_3','PPP')),
            Bill("04-11-2023","03-12-2023",1346,152_155,Curr.CLP,('BT','_3','PPP')),
            Bill("04-12-2023","03-01-2024",1346,162_554,Curr.CLP,('BT','_3','PPP')),          
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W MOD 01',
                quantity=9,
                orientation=Orientation(35,28),
                ),
            PvInput(
                description='FV 655W MOD 02',
                quantity=11,
                orientation=Orientation(20,28),
                ),
            PvInput(
                description='FV 655W MOD 03',
                quantity=4,
                orientation=Orientation(10,28),
            )
        ),
        'install':(
            'instalación',
            repoEquipment['Inverter']['DY 12kW H'],# inverter
            repoEquipment['Medidor']['FR 3F'],# lectura
            Equip(
                description='eléctrica interior',
                specification=Specs(
                    category='Obra',
                    brand='conexionado',
                    model='interiores'
                    ),
                cost_per_unit=Cost(225_000,Curr.CLP),
                quantity=16#power kW
            ),
            Equip(
                description='estructura montaje',
                specification=Specs(
                    category='Montaje',
                    montaje='coplanar',
                    ),
                cost_per_unit=Cost(45_000,Curr.CLP),
                quantity=24#panels
                ),
            ),
        'storage':(
            'almacenamiento',4,'24/5',
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
                cost_per_unit=Cost(18_750,Curr.CLP),
                quantity=24#panels
                ),
            Equip(
                description='Capacitación',
                specification=Specs(
                    category='Obra',
                    brand='Uso y',
                    model='mantenimiento',
                    taller='2 Hrs',
                    manual='3 u. impreso',
                    ),
                cost_per_unit=Cost(250_000,Curr.CLP),
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
                cost_per_unit=Cost(450_000,Curr.CLP),
                )
        ),
        'overloads':{
            'gastos_gral':15,
            'utilidad':10
        }
    }
}