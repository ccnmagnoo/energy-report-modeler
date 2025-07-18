"""permanent project data"""
#cspell: disable
from typing import Literal
from models.components import Component as Equip, Specs, Tech
from models.consumption import ElectricityBill as Bill
from models.econometrics import Cost, Currency as Curr
from models.geometry import Orientation
from models.inventory import Building
from models.photovoltaic import PvInput
from libs.repository import warehouse,panelRepo

type Subject = Literal['project','consumptions','components']

#gen
PANELS:int=80
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'Sistema ERNC SSVSA',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.04401, -71.62143),
            name='Edificio SSVSA',
            address='Av. Brasil 1435',
            city='Valparaíso'),
    },
    'consumptions':{
        'cost_increment':5.8,
        'client_id':'672250-4',
        'measurer_id':'10034493',
        'contract_id':'BT-3 PP',
        'consumption':[
            Bill("13-11-2023","12-12-2023",15_720,1_495_284,Curr.CLP,('BT','_3','PP'),p_leida=53.3,dmax=80.7),#costo_dmax=1_601_133),
            Bill("12-12-2023","11-01-2024",15_660,1_487_594,Curr.CLP,('BT','_3','PP'),p_leida=53.5,dmax=80.7),#costo_dmax=1.601_133),
            Bill("11-01-2024","09-02-2024",16_560,1_573_087,Curr.CLP,('BT','_3','PP'),p_leida=59.2,dmax=80.7),#costo_dmax=1_601_133),
            Bill("09-02-2024","11-03-2024",15_900,1_510_934,Curr.CLP,('BT','_3','PP'),p_leida=51.7,dmax=80.7),#costo_dmax=1_601_133),
            Bill("11-03-2024","11-04-2024",16_680,1_584_487,Curr.CLP,('BT','_3','PP'),p_leida=53.0,dmax=80.7),#costo_dmax=1_601_133),
            Bill("11-04-2024","13-05-2024",17_880,1_698_480,Curr.CLP,('BT','_3','PP'),p_leida=66.8,dmax=80.7),#costo_dmax=1_601_133),
            Bill("13-05-2024","11-06-2024",17_580,1_761_547,Curr.CLP,('BT','_3','PP'),p_leida=67.6,dmax=80.7),#costo_dmax=1_779_615),
            Bill("11-06-2024","11-07-2024",19_020,2_423_419,Curr.CLP,('BT','_3','PP'),p_leida=81.1,dmax=81.1),#costo_dmax=1_812_578),
            Bill("11-07-2024","11-08-2024",20_460,2_606_897,Curr.CLP,('BT','_3','PP'),p_leida=82.0,dmax=82.0),#costo_dmax=1_823_287),
            Bill("04-08-2024","03-09-2024",19_980,2_163_495,Curr.CLP,('BT','_3','PP'),p_leida=72.6,dmax=81.6),#costo_dmax=1_819_721),
            Bill("03-09-2024","09-10-2024",16_080,2_188_191,Curr.CLP,('BT','_3','PP'),p_leida=59.2,dmax=81.6),#costo_dmax=1_926_901),
            Bill("09-10-2024","11-11-2024",17_940,2_411_302,Curr.CLP,('BT','_3','PP'),p_leida=55.9,dmax=81.6),#costo_dmax=1_925_662),
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W MOD 01',
                quantity=40,
                orientation=Orientation(15,-90+19),
                ),
            PvInput(
                description='FV 655W MOD 02',
                quantity=40,
                orientation=Orientation(15,-90+19+180),
                ),
        ),
        'install':(
            'instalación',
            warehouse['Inverter']['CS 50kW H'],# inverter
            warehouse['Medidor']['FR 3F'],# lectura
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
            warehouse['Monitor']['VC 700'],
            warehouse['Regulator']['VT 45A']
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
            'gastos_gral':15,
            'utilidad':10
        }
    }
}