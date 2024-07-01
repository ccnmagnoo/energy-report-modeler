from typing import Literal
from models.components import Component
from models.econometrics import Cost, Currency
from models.geometry import Orientation
from models.photovoltaic import Length, PvTechnicalSheet

#cspell: disable

repo = {
    'inverter':{
        'Solis 2.5kW':Component('Inversor ongrid 2.5kW',
                model='Solis Mini 2500 4G',
                reference='https://www.solartex.cl/tienda/producto/inversor-grid-tie-mini-2-5-kw-4g-monofasico-solis/',
                specification='Ongrid 2.5kW Monofásico',
                cost_per_unit=Cost(557000,Currency.CLP)
                ),
        'Huawei 3WK':Component('Inversor ongrid 3kW',
                model='Huawei SUN2000 3KTL',
                reference='https://www.solartex.cl/tienda/producto/inversor-grid-tie-3kw-sun2000-3ktl-huawei/',
                specification='Ongrid 3kW Monofásico',
                cost_per_unit=Cost(1002800,Currency.CLP)
                ),
        'Voltronic 3kW':Component('Inversor ongrid 3kW',
                model='Voltronic 3kW 48V',
                reference='https://www.tiendatecnored.cl/inversor-string-canadian-solar-3kw.html',
                specification='Ongrid 3kW Monofásico',
                cost_per_unit=Cost(511290,Currency.CLP)
                ),
        'Solis 3.6kW':Component('Inversor ongrid 3.6kW',
                model= 'Solis-S6GR1PM 3.6kW',
                reference='https://www.solartex.cl/tienda/producto/inversor-grid-tie-sun2000-4ktl-4kw-huawei/',
                specification='Solis Tie 3.6kW Solist',
                cost_per_unit=Cost(612000,currency=Currency.CLP),
                ),
        'Huawei 4kW':Component('Inversor - ongrid 4kW',
                model= 'Huawei SUN2000L-4KTL L1',
                reference='https://www.solartex.cl/tienda/producto/inversor-grid-tie-sun2000-4ktl-4kw-huawei/',
                specification='On-grid 4kW Monofásico',
                cost_per_unit=Cost(1227050,currency=Currency.CLP),
                ),
        'Voltronic 5kW':Component('Inversor Híbrido',
                model='Voltronic 5kW 48V',
                reference='https://solarbex.com/comprar/inversor-hibrido-5kw-48v-axpert/',
                specification='Híbrido 5kW Monofásico',
                cost_per_unit=Cost(869,Currency.EUR)
                ),
        'Solis 6kW':Component('Inversor Híbrido',
                model='Solis RHI-6K-48ES-5G',
                reference='https://www.solartex.cl/tienda/producto/inversor-hibrido-6kw-48v-solis-rhi-5g/',
                specification='Híbrido 6kW 48V',
                cost_per_unit=Cost(2109600,Currency.CLP)
                ),
        'Voltronic 7kW':Component('Inversor Híbrido',
        model='Voltronic 7kW 48V',
        reference='https://solarbex.com/comprar/inversor-hibrido-7kw-48v-voltronic/',
        specification='Híbrido 7kW Monofásico',
        cost_per_unit=Cost(1255,Currency.EUR)
        ),
        'Solis 8kW':Component('Inversor Híbrido',
        model='Solis S6-EH10 48V',
        reference='https://www.solartex.cl/tienda/producto/inversor-hibrido-8kw-solis-s6-eh1p8k-l-pro/',
        specification='Híbrido 8kW 48V',
        cost_per_unit=Cost(2184000,Currency.CLP)
        ),
        'Solis 10kW':Component('Inversor Híbrido 10kW',
        model='Solis RHI 3P10K',
        reference='https://www.solartex.cl/tienda/producto/inversor-hibrido-trifasico-10kw-solis-rhi-3p10k-hves-5g/',
        specification='Híbrido 10kW 3FASE 48V',
        cost_per_unit=Cost(3735817,Currency.CLP)
        ),
        'Deye 12kW':Component('Inversor Híbrido Trifásico',
        model='Deye Sun 12kW 380V',
        reference='https://solarbex.com/comprar/inversor-hibrido-deye-12kw-trifasico/',
        specification='Híbrido 12kW Trifásico',
        cost_per_unit=Cost(3190,Currency.EUR)
        ),
    },
    'panel':{
        '655w' : {
                'reference':'https://www.tiendatecnored.cl/modulo-fotovoltaico-650w-canadian-solar.html',
                'specification':'Solar Panel PV 655w',
                'model':'Canadian Solar 655w',
                'cost':Cost(248171/1.19,Currency.CLP),
                'technical_sheet':PvTechnicalSheet(power=655,area=(130.3,238.4,Length.CM)),
        },
        '375w' : {
                'reference':'https://www.tiendatecnored.cl/panel-solar-375w-canadian-solar.html',
                'specification':'Solar Panel PV 374w',
                'model':'Canadian Solar 375w',
                'cost':Cost(146509/1.19,Currency.CLP),
                'technical_sheet':PvTechnicalSheet(power=375,area=(104.8,176.5,Length.CM)),
        },
        '455w' : {
                'reference':'https://www.tiendatecnored.cl/modulo-fotovoltaico-455w-zn-shine.html',
                'specification':'Solar Panel PV 374w MONO',
                'model':'SHINE ZN ZXM6-NH144 455w',
                'cost':Cost(116502/1.19,Currency.CLP),
                'technical_sheet':PvTechnicalSheet(power=455,area=(104.8,209.4,Length.CM)),
        },
    }
}