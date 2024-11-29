from typing import Literal
from models.components import Component, Specs
from models.econometrics import Cost, Currency
from models.photovoltaic import Length, PvFactory, PvTechnicalSheet

#cspell: disable

type EquipType = Literal['inverter','panel','charger','labor','montage']
type EquipDef = str
type Repo = dict[EquipType:dict[EquipDef,Component]]
type Panel = dict[EquipDef,PvFactory]


repo:Repo = {
        'inverter':{
        'HW 2kW':Component(
                description='Inversor ongrid 2kW',
                specification=Specs(
                        'Inverter',
                        'Huawei',
                        'Sun2000-2KLT-L1',
                        'https://www.dartel.cl/inversor-huawei-on-grid-2kw-hibrido-monofasico-sun2000-2ktl-l1-2088128161-huawei/p',
                        'https://imagenes.dartel.cl/2088128161/FICHA/FICHA_2088128161.pdf',
                        mode='on-grid',
                        power='2kW',
                        input='220V',
                        fase='Monofase',
                        MPPT_r='90-560V',
                        MPPT='1/1'
                        ),
                cost_per_unit=Cost(678_809,Currency.CLP)
                ),
        'SL 2.5kW':Component(
                description='Inversor ongrid 2.5kW',
                specification=Specs(
                        'Inverter',
                        'Solis',
                        'Mini 2500 4G',
                        'https://www.solartex.cl/tienda/producto/inversor-grid-tie-mini-2-5-kw-4g-monofasico-solis/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/06/Solis-mini-700-3600-4G.pdf',
                        mode='on-grid',
                        power='2.5kW',
                        input='330V',
                        fase='Monofase',
                        MPPT_r='80-500V',
                        ),
                cost_per_unit=Cost(557_000,Currency.CLP)
                ),
        'HW 3WK':Component(
                description='Inversor ongrid 3kW',
                specification=Specs(
                        'Inverter',
                        'Huawei',
                        'SUN2000-3KTL',
                        'https://www.solartex.cl/tienda/producto/inversor-grid-tie-3kw-sun2000-3ktl-huawei/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2019/07/FICHA-TECNICA-PDF.jpg',
                        mode='on-grid',
                        power='3KWp',
                        input='600V',
                        fase='Mono',
                        MPPT_r='90-600V',
                        ),
                cost_per_unit=Cost(1_002_800,Currency.CLP)
                ),
        'IS 3kW':Component(
                description='Inversor Hibrido 3kW',
                specification=Specs(
                        'Inverter',
                        'InfiniSolar',
                        'V 3KW 48V',
                        'https://www.solartex.cl/tienda/producto/inversor-hibrido-infinisolar-v-3kw-48v/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2019/07/V.INF_.P.3K-48.pdf',
                        mode='Hybrid',
                        power='3KWp',
                        volt='145VDC',
                        fase='Mono',
                        MPPT_r='90-600V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(675_625,Currency.CLP)
                ),
        'CS 3kW':Component(
                description='Inversor Ongrid 3kW',
                specification=Specs(
                        'Inverter',
                        'Canadian Solar',
                        'CSI-700TL1P-GI-FL',
                        'https://www.tiendatecnored.cl/inversor-string-canadian-solar-3kw.html',
                        'https://www.tiendatecnored.cl/media/wysiwyg/ficha-tecnica/7404406_110520.pdf',
                        mode='on-grid',
                        power='3KWp',
                        volt='600V',
                        fase='Mono',
                        MPPT_r='234-500V',
                        ),
                cost_per_unit=Cost(511_290,Currency.CLP)
                ),
        'HW 4kW':Component(
                description='Inversor Ongrid 4kW',
                specification=Specs(
                        'Inverter',
                        'Huawei',
                        'SUN2000L-4KTL L1',
                        'https://www.solartex.cl/tienda/producto/inversor-grid-tie-sun2000-4ktl-4kw-huawei/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2019/07/FICHA-TECNICA-PDF.jpg',
                        mode='on-grid',
                        power='4KWp',
                        volt='600V',
                        fase='Mono',
                        MPPT_r='210-480V',
                        ),
                specification='On-grid 4kW Monofásico',
                cost_per_unit=Cost(1_227_050,currency=Currency.CLP),
                ),
        'VT 5kW':Component(
                description='Inversor Híbrido 5KW',
                specification=Specs(
                        'Inverter',
                        'Voltronic',
                        'Axpert VMIII 5kW',
                        'https://www.naturaenergy.cl/product/inversor-cargador-voltronic-axpert-vm-iii-48v-5000va-5000w',
                        'https://s3.amazonaws.com/bsalemarket/10729/1/AD5273(1).pdf',
                        mode='Hybrid',
                        power='5KWp',
                        volt='500V',
                        fase='Mono',
                        MPPT_r='90-280V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(487_387,Currency.CLP)
                ),
        'SL 6kW':Component(
                description='Inversor Híbrido 6kW',
                specification=Specs(
                        'Inverter',
                        'Solis',
                        '6KW RHI-48ES-5G',
                        'https://www.solartex.cl/tienda/producto/inversor-hibrido-6kw-48v-solis-rhi-5g/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/06/Ficha-de-datos-RHI-3-6K-48ES-5G.pdf',
                        mode='Hybrid',
                        power='6KWp',
                        volt='500V',
                        fase='Mono',
                        MPPT_r='90-280V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(2_109_600,Currency.CLP)
                ),
        'VT 7kW':Component(
                description='Inversor Hibrido 7.2kW',
                specification=Specs(
                        'Inverter',
                        'Voltronic',
                        'Axpert Max7200W',
                        'https://www.naturaenergy.cl/product/inversor-cargador-voltronic-axpert-max-48v-7200w-con-mppt-dual-8000w-pv',
                        'https://s3.amazonaws.com/bsalemarket/10729/3/AD2211-FICHA-TECNICA-INVERSOR-AEXPERTMAX',
                        mode='Hybrid',
                        power='7.2KWp',
                        volt='500V',
                        fase='Mono',
                        MPPT_r='80a/500V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(878_143,Currency.CLP),
        ),
        'SL 8kW':Component(
                description='Inversor Híbrido 8kW',
                specification=Specs(
                        'Inverter',
                        'Solis',
                        'S6-EH1P8K-L Pro',
                        'https://www.solartex.cl/tienda/producto/inversor-hibrido-8kw-solis-s6-eh1p8k-l-pro/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2024/03/S6-EH1P8K-LP.pdf',
                        mode='Hybrid',
                        power='8KWp',
                        volt='230VAC',
                        fase='Mono',
                        MPPT_r='90-450VDC',
                        battery='48V'
                        ),
                cost_per_unit=Cost(2_184_000,Currency.CLP)
        ),
        'SL 10kW':Component(
                description='Inversor Híbrido 10kW',
                specification=Specs(
                        'Inverter',
                        'Solis',
                        'RHI-3P10K',
                        'https://www.solartex.cl/tienda/producto/inversor-hibrido-trifasico-10kw-solis-rhi-3p10k-hves-5g/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/06/Solis_datasheet_RHI-3P5-10K-HVES-5G_AUS.pdf',
                        mode='Hybrid',
                        power='10KW',
                        volt='1000V',
                        fase='3|f',
                        MPPT_r='200-850V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(3_735_817,Currency.CLP)
        ),
        'DY 12kW':Component(
                description='Inversor Híbrido 3/F 12kW',
                specification=Specs(
                        'Inverter',
                        'Deye',
                        'SUN-12K-SG04L P3-EU',
                        'https://solarbex.com/comprar/inversor-hibrido-deye-12kw-trifasico/',
                        'https://solarbex.com/wp-content/uploads/2023/09/DEYE-HYBRID-TRIFASICO-10K-12K.pdf',
                        mode='Hybrid',
                        power='12KWp',
                        volt='500V',
                        fase='Mono',
                        MPPT_r='80a/650V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(3_190,Currency.EUR)
        ),
        'CS 15kW':Component(
                description='Inversor Híbrido 3/F 15kW',
                specification=Specs(
                        'Inverter',
                        'Solar Canadian',
                        'CSI-15K-T400GL01-E',
                        'https://www.tiendatecnored.cl/inversor-canadian-solar-15kw-trifasico.html',
                        'https://solarbex.com/wp-content/uploads/2023/09/DEYE-HYBRID-TRIFASICO-10K-12K.pdf',
                        mode='Hybrid',
                        power='15KWp',
                        volt='500V',
                        fase='3|f',
                        MPPT_r='80a/650V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(1_252_450,Currency.CLP)
        ),
        'DY 30kW':Component(
                description='Inversor Híbrido 3/F 30kW',
                specification=Specs(
                        'Inverter',
                        'Deye',
                        'SUN-30K SG01HP3',
                        'https://solarbex.com/comprar/inversor-hibrido-deye-30kw-trifasico-alto-voltaje/',
                        'https://solarbex.com/wp-content/uploads/2023/08/SUN-25-50K-SG01HP3-EU.pdf',
                        mode='Hybrid',
                        power='30KWp',
                        volt='500V',
                        fase='3|f',
                        MPPT_r='80a/650V',
                        battery='48V'
                        ),
        cost_per_unit=Cost(5_995,Currency.EUR)
        ),
        'CS 50kW':Component('Inversor Híbrido 3/F 50kW',
                specification=Specs(
                        'Inverter',
                        'Canadian Solar',
                        'CSI-50K-T400GL03-E',
                        'https://www.solartex.cl/tienda/producto/inversor-grid-tie-50kw-trifasico-canadian-solar/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/05/INVERSOR-CANADIAN-CSI-50K-T400.pdf',
                        mode='Hybrid',
                        power='50KWp',
                        volt='500V',
                        fase='3|f',
                        MPPT_r='80a/650V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(4_690_000,Currency.CLP)
        ),
        'CS 100kW':Component('Inversor Híbrido 3/F 100kW',
                specification=Specs(
                        'Inverter',
                        'Canadian Solar',
                        'CSI-100K-T400GL02-E',
                        'https://www.solartex.cl/tienda/producto/inversor-grid-tie-100kw-trifasico-canadian-solar/',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/05/CANADIAN-SOLAR-CSI-100K-T400GL02-E.pdf',
                        mode='Hybrid',
                        power='100KWp',
                        volt='1100V',
                        fase='3|f',
                        MPPT_r='180-1000V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(8_680_000,Currency.CLP)
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

panelRepo:Panel = {
        'CS 655W':PvFactory(
                specs=Specs(
                        category='Photovoltaic',
                        brand='Canadian solar',
                        model='CS7N-655',
                        ref_url='https://www.tiendatecnored.cl/modulo-fotovoltaico-650w-canadian-solar.html',
                        specs_url='https://static.csisolar.com/wp-content/uploads/sites/3/2021/07/28105634/CS-BiHiKu7_CS7N-MB-AG_v1.7_F43M_J1_NA.pdf',
                        power='655W',
                        cristal='Mono',
                        Vmpp='38.12V',
                        Impp='17.32A',
                        ef='21.2%'

                ),
                cost=Cost(248_171/1.19,Currency.CLP),
                technical_sheet=PvTechnicalSheet(power=655,area=(130.3,238.4,Length.CM))
        ),
        'RS 650W':PvFactory(
                specs=Specs(
                        category='Photovoltaic',
                        brand='Risen',
                        model='CS7N-655',
                        ref_url='https://www.solartex.cl/tienda/producto/panel-solar-660-watts-risen-mono-perc-half-cells/',
                        specs_url='https://www.solartex.cl/tienda/wp-content/uploads/2023/03/RSM132-8-660M.pdf',
                        power='650 W',
                        cristal='Mono',
                        Vmpp='38.12 V',
                        Impp='17.32 A',
                        ef='21.2%',
                ),
                cost=Cost(288_000,Currency.CLP),
                technical_sheet=PvTechnicalSheet(power=650,area=(130.3,238.4,Length.CM))
        ),
        'ZN 455W':PvFactory(
                specs=Specs(
                        category='Photovoltaic',
                        brand='ZN Shine',
                        model='ZXM6-NH144',
                        ref_url='https://www.solartex.cl/tienda/producto/panel-solar-660-watts-risen-mono-perc-half-cells/',
                        specs_url='https://znshinesolar.gr/wp-content/uploads/ZXM6-NH144-min.pdf',
                        power='455W',
                        cristal='Mono',
                        Vmpp='41.60 V',
                        Impp='10.94 A',
                        ef='20.93%',
                ),
                cost=Cost(116_502,Currency.CLP),
                technical_sheet=PvTechnicalSheet(power=455,area=(103.8,209.4,Length.CM))
        ),
        'CS 375W':PvFactory(
                specs=Specs(
                        category='Photovoltaic',
                        brand='Canadian Solar',
                        model='CS3L375MS ',
                        ref_url='https://www.tiendatecnored.cl/panel-solar-375w-canadian-solar.html',
                        specs_url='https://www.tiendatecnored.cl/media/wysiwyg/ficha-tecnica/4703157.pdf',
                        power='375W',
                        cristal='MonoSI',
                        Vmpp='41.0 V',
                        Impp='11.61 A',
                        ef='20.3%',
                ),
                cost=Cost(190_448/1.19,Currency.CLP),
                technical_sheet=PvTechnicalSheet(power=375,area=(104.8,176.5,Length.CM))
        ),
}