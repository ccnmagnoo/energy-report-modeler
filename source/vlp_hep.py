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
PANELS:int=3*21+2*4+2*21
POWER:int=PANELS*655/1000
#

data:dict[Subject,any] = {
    'project':{
        'title':'FV H. E.Pereira R.',
        'connection_type':'netbilling',
        'technology':[Tech.PHOTOVOLTAIC],
        'building':Building(
            geolocation=(-33.056764, -71.589541),
            name='H. Dr. Eduardo Pereira',
            address='Ibsen S/N',
            city='Valparaíso'),
    },
    'consumptions':{
        'cost_increment':4.7,
        'client_id':'250837-0',
        'measurer_id':'10033891',
        'contract_id':'AT-4.3 ',
        'consumption':[
            Bill("11-04-2024","13-05-2024",81_480,9_550805,Curr.CLP,('AT','_43','NA'),Dms=203.3,Dmhp=111.7),
            Bill("13-05-2024","11-06-2024",78_400,9_375183,Curr.CLP,('AT','_43','NA'),Dms=198.2,Dmhp=115.4),
            Bill("11-06-2024","11-07-2024",82_040,12235857,Curr.CLP,('AT','_43','NA'),Dms=213.1,Dmhp=118.4),
            Bill("11-07-2024","12-08-2024",89_040,13991898,Curr.CLP,('AT','_43','NA'),Dms=218.4,Dmhp=206.4),
            Bill("12-08-2024","09-09-2024",75_040,12140939,Curr.CLP,('AT','_43','NA'),Dms=206.4,Dmhp=110.6),
            Bill("09-09-2024","09-10-2024",75_040,13024816,Curr.CLP,('AT','_43','NA'),Dms=189.3,Dmhp=101.6),
            Bill("09-10-2024","11-11-2024",83_160,13976540,Curr.CLP,('AT','_43','NA'),Dms=185.4,Dmhp=0),
            Bill("11-11-2024","10-12-2024",68_320,11880503,Curr.CLP,('AT','_43','NA'),Dms=183.1,Dmhp=0),
            Bill("10-12-2024","10-01-2025",70_280,12307253,Curr.CLP,('AT','_43','NA'),Dms=161.8,Dmhp=0),
            Bill("10-01-2025","12-02-2025",76_160,13470140,Curr.CLP,('AT','_43','NA'),Dms=169.4,Dmhp=0),
            Bill("12-02-2025","12-03-2025",65_800,12066719,Curr.CLP,('AT','_43','NA'),Dms=166.0,Dmhp=0),
            Bill("12-03-2024","11-04-2025",73_080,13050247,Curr.CLP,('AT','_43','NA'),Dms=174.7,Dmhp=105.3)
        ]
    },
    'components':{
        'generator':(
            panelRepo['CS 655W'],# equipment
            PvInput(
                description='FV 655W mod01',
                quantity=3*21,
                orientation=Orientation(5,20),
                ),
            PvInput(
                description='FV 655W mod02',
                quantity=4*2,
                orientation=Orientation(5,20),
                ),
            PvInput(
                description='FV 655W mod03',
                quantity=2*21,
                orientation=Orientation(15,35),
                ),
        ),
        'install':(
            'instalación',
            warehouse['Inverter']['CS 100kW H'],# inverter
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
                cost_per_unit=Cost(55_000),
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
            'gastos_gral':30,
            'utilidad':20
        }
    }
}