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
PANELS:int=24
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'Sistema FV Waddington',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.027817, -71.633331),
            name='Loft_Waddington',
            address='Avda. Waddington 290, Playa Ancha',
            city='Valparaíso'),
    },
    'consumptions':{
        'cost_increment':5.8,
        'client_id':'672250-4',
        'measurer_id':'51648355',
        'contract_id':'BT-3 PPP',
        'consumption':[
            Bill("19-02-2024","20-03-2024",1_913,181_722,Curr.CLP,('BT','_3','PPP'),p_leida=8.0,dmax=8.5),#costo_dmax=1_601_133),
            Bill("20-03-2024","19-04-2024",1_781,169_183,Curr.CLP,('BT','_3','PPP'),p_leida=8.7,dmax=8.7),#costo_dmax=1.601_133),
            Bill("19-04-2024","22-05-2024",1_956,184_857,Curr.CLP,('BT','_3','PPP'),p_leida=8.6,dmax=8.7),#costo_dmax=1_601_133),
            Bill("22-05-2024","21-06-2024",1_816,181_966,Curr.CLP,('BT','_3','PPP'),p_leida=9.2,dmax=9.2),#costo_dmax=1_601_133),
            Bill("21-06-2024","22-07-2024",1_814,231_130,Curr.CLP,('BT','_3','PPP'),p_leida=8.5,dmax=9.0),#costo_dmax=1_601_133),
            Bill("22-07-2024","21-08-2024",1_782,227_053,Curr.CLP,('BT','_3','PPP'),p_leida=8.3,dmax=9.0),#costo_dmax=1_601_133),
            Bill("21-08-2024","17-09-2024",1_518,193_416,Curr.CLP,('BT','_3','PPP'),p_leida=9.3,dmax=9.3),#costo_dmax=1_779_615),
            Bill("17-09-2024","17-10-2024",2_111,287_268,Curr.CLP,('BT','_3','PPP'),p_leida=9.8,dmax=9.8),#costo_dmax=1_812_578),
            Bill("04-08-2024","03-09-2024",2_396,326_051,Curr.CLP,('BT','_3','PPP'),p_leida=9.2,dmax=9.3),#costo_dmax=1_819_721),
            Bill("03-09-2024","09-10-2024",2_064,280_872,Curr.CLP,('BT','_3','PPP'),p_leida=8.7,dmax=9.3),#costo_dmax=1_926_901),
            Bill("19-12-2024","20-01-2025",2_235,321_441,Curr.CLP,('BT','_3','PPP'),p_leida=10.4,dmax=10.4),#costo_dmax=1_925_662),
            Bill("20-01-2025","20-02-2025",2_491,347_636,Curr.CLP,('BT','_3','PPP'),p_leida=10.4,dmax=10.4),#costo_dmax=1_823_287),
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W mod A',
                quantity=12,
                orientation=Orientation(10,0),
                ),
            PvInput(
                description='FV 655W mod B',
                quantity=12,
                orientation=Orientation(23,0),
                ),

        ),
        'install':(
            'instalación',
            repoEquipment['Inverter']['CS 15kW H'],# inverter
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
        ),
        'overloads':{
            'gastos_gral':15,
            'utilidad':10
        }
    }
}