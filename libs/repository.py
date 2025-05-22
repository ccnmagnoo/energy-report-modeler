from models.components import Component, Specs,EquipmentCategory
from models.econometrics import Cost, Currency
from models.photovoltaic import Cell, Length, PowerCurve, PvFactory, PvTechnicalSheet

#cspell: disable

type EquipDef = str
type Repo = dict[EquipmentCategory:dict[EquipDef,Component]]
type Panel = dict[EquipDef,PvFactory]


repoEquipment:Repo = {
        'Inverter':{
        'HW 2kW OG':Component(
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
        'SL 2.5kW OG':Component(
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
        'HW 3WK OG':Component(
                description='Inversor on-grid 3kW',
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
        'IS 3kW H':Component(
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
        'CS 3kW OG':Component(
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
        'HW 4kW OG':Component(
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
                cost_per_unit=Cost(1_227_050,currency=Currency.CLP),
                ),
        'VT 5kW HY':Component(
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
        'SL 6kW HY':Component(
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
        'SL 10kW H':Component(
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
        'KT 10kW H':Component(
                description='Inversor Híbrido 10kW',
                specification=Specs(
                        'Inverter',
                        'Kehua Tech',
                        'ISTORAGE3 10K',
                        'https://rhona.cl/producto/11232/inversor-hibrido-trifasico-10kw.html',
                        'https://www.solartex.cl/tienda/wp-content/uploads/2023/06/Solis_datasheet_RHI-3P5-10K-HVES-5G_AUS.pdf',
                        mode='Hybrid',
                        power='10KW',
                        volt='1000Vdc',
                        fase='3|f',
                        MPPT_r='150-900V',
                        battery='48V'
                        ),
                cost_per_unit=Cost(3_459_656,Currency.CLP)
        ),
        'DY 12kW H':Component(
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
        'CS 15kW H':Component(
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
        'DY 30kW H':Component(
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
        'KH 25kW':Component(
                description='Inversor Ongrid 3/F 25kW',
                specification=Specs(
                        'Inverter',
                        'Kehua',
                        'SPI25K-B-X2',
                        'https://rhona.cl/producto/11229/inversor-on-grid-trifasico-25kw.html',
                        'https://rhona.cl/producto/11229/inversor-on-grid-trifasico-25kw.html',
                        mode='ON-GRID',
                        power='25KWp',
                        volt='600V',
                        fase='3|f',
                        MPPT_r='180a/1100V',
                        ),
        cost_per_unit=Cost(2_114_111,Currency.CLP)
        ),
        'CS 50kW H':Component('Inversor Híbrido 3/F 50kW',
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
        'CS 100kW H':Component('Inversor Híbrido 3/F 100kW',
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
        'Medidor':{
                'EL 1F':Component(# medidor
                description='Medidor 1/Fase 240V ',
                specification=Specs(
                        category='Medidor',
                        brand='Elster',
                        model='A150',
                        ref_url='https://www.solartex.cl/tienda/producto/medidor-bidireccional-monofasico-elster-a150/',
                        specs_url='https://www.solartex.cl/tienda/producto/medidor-bidireccional-monofasico-elster-a150/#tab-description',
                        Red='1 fase',
                        Voltaje='120-240 V',
                        Frec='50/60 Hz',
                        Imax='60A',
                        Pmax='14.4 kW',
                        ),
                cost_per_unit=Cost(93_450,Currency.CLP)),
                'FR 3F':Component(# medidor
                description='Medidor 3/Fases 400V',
                specification=Specs(
                        category='Medidor',
                        brand='Fronius',
                        model='SMMT-TRIF-50kA',
                        ref_url='https://www.solartex.cl/tienda/producto/smart-meter-fronius-50ka-trifasico-indirecto/',
                        specs_url='https://www.solartex.cl/tienda/producto/smart-meter-fronius-50ka-trifasico-indirecto/#tab-description',
                        Red='trifásico',
                        Voltaje='400-415 V',
                        Imax='3 x 50kA',
                        Section='0.05-4 mm2',
                ),
                cost_per_unit=Cost(353_050,Currency.CLP)
                ),
        },
        'Monitor':{
                'VC 700':Component(
                        description='Monitor de carga',
                        specification=Specs(
                                category='Storage',
                                brand='Victron',
                                model='BMV-700',
                                ref_url='https://www.solarstore.cl/producto/monitor-de-baterias-victron-bmv-700/',
                                specs_url='https://www.solarstore.cl/wp-content/uploads/2019/10/Victron-BMV-700-series-ES.pdf',
                                Rango="6.5-95Vdc",
                                Cap='1-9999 Ah'
                ),
                cost_per_unit=Cost(150_000/1.19,Currency.CLP)
                ),
                'VC 712':Component(
                        description='Monitor de carga',
                        specification=Specs(
                                category='Storage',
                                brand='Victron',
                                model='BMV-712 smart',
                                ref_url='https://www.solarstore.cl/producto/monitor-de-baterias-victron-bmv-712-bluetooth/',
                                specs_url='https://www.solarstore.cl/wp-content/uploads/2023/06/Victron-BMV-712-Smart.pdf',
                                Rango="6.5-70Vcc",
                                Cap='1-9999 Ah'
                ),
                cost_per_unit=Cost(200_000/1.19,Currency.CLP)
                ),

        },
        'Regulator':{
                'VT 45A':Component(
                description='Regulador',
                specification=Specs(
                        category='Charge Regulator',
                        brand='Victron',
                        model='Bluesolar 150/45-Tr',
                        ref_url='https://www.solarstore.cl/producto/controlador-de-carga-victron-bluesolar-45a-12-24-36-48v-mppt/',
                        specs_url='https://www.solarstore.cl/producto/controlador-de-carga-victron-bluesolar-45a-12-24-36-48v-mppt/Datasheet-BlueSolar-charge-controller-MPPT-150-35-&-150-45-ES',
                        Volt='12/24/36/48V',
                        Inom='45 A',
                ),
                cost_per_unit=Cost(370_000/1.19,Currency.CLP)
                ),
                'VT 60A':Component(
                description='Regulador',
                specification=Specs(
                        category='Charge Regulator',
                        brand='Victron',
                        model='Bluesolar 150/45-Tr',
                        ref_url='https://www.solarstore.cl/producto/controlador-de-carga-victron-bluesolar-60a-12-24-36-48v-mppt-copia/',
                        specs_url='https://www.solarstore.cl/wp-content/uploads/2023/10/Datasheet-BlueSolar-charge-controller-MPPT-150-60-and-150-70-ES.pdf',
                        Volt='12/24/36/48V',
                        Inom='60 A',
                ),
                cost_per_unit=Cost(490_000/1.19,Currency.CLP)
                ),
        },
}

panelRepo:Panel = {
        'CS 655W':PvFactory(
                cost=Cost(248_171/1.19,Currency.CLP),
                technical_sheet=PvTechnicalSheet(
                        brand='Canadian solar',
                        model='CS7N-655',
                        power=655,
                        area=(103.8,238.4,Length.CM),
                        efficiency=21.2,
                        ref_url='https://www.tiendatecnored.cl/modulo-fotovoltaico-650w-canadian-solar.html',
                        specs_url='https://static.csisolar.com/wp-content/uploads/sites/3/2021/07/28105634/CS-BiHiKu7_CS7N-MB-AG_v1.7_F43M_J1_NA.pdf',
                        power_curve=PowerCurve(
                                max_tension=38.1,
                                short_tension=45.2,
                                max_ampere=17.20,
                                short_ampere=18.43
                                ),
                        cell=Cell(row=6,col=11,group=2)
                        )
        ),
        'CS 650W':PvFactory(
                cost=Cost(299_250/1.19,Currency.CLP),
                technical_sheet=PvTechnicalSheet(
                        brand='Canadian solar',
                        model='CS7N-650',
                        power=650,
                        area=(103.8,238.4,Length.CM),
                        efficiency=20.9,
                        ref_url='https://www.citysun.cl/producto/panel-solarcanadian-solar-650wp/',
                        specs_url='https://www.citysun.cl/wp-content/uploads/2021/10/Ficha-Tecnica-canadian-650wp.pdf',
                        power_curve=PowerCurve(
                                max_tension=37.9,
                                short_tension=45.0,
                                max_ampere=17.16,
                                short_ampere=18.38
                                ),
                        cell=Cell(row=6,col=11,group=2)
                        )
        ),
        'RS 660W':PvFactory(
                cost=Cost(288_000,Currency.CLP),
                technical_sheet=PvTechnicalSheet(
                        brand='Risen',
                        model='RSM132-8-660M',
                        power=660,
                        area=(103.8,238.4,Length.CM),
                        efficiency=21.2,
                        ref_url='https://www.solartex.cl/tienda/producto/panel-solar-660-watts-risen-mono-perc-half-cells/',
                        specs_url='https://www.solartex.cl/tienda/wp-content/uploads/2023/03/RSM132-8-660M.pdf',
                        power_curve=PowerCurve(
                                max_tension=38.12,
                                short_tension=45.75,
                                max_ampere=17.32,
                                short_ampere=18.33
                                ),
                        cell=Cell(row=11,col=6,group=2)
                        )
        ),
        'ZN 455W':PvFactory(
                cost=Cost(116_502,Currency.CLP),
                technical_sheet=PvTechnicalSheet(
                        brand='ZN Shine',
                        model='ZXM6-NH144',
                        power=455,
                        area=(103.8,209.4,Length.CM),
                        efficiency=20.93,
                        ref_url='https://www.solartex.cl/tienda/producto/panel-solar-660-watts-risen-mono-perc-half-cells/',
                        specs_url='https://znshinesolar.gr/wp-content/uploads/ZXM6-NH144-min.pdf',
                        power_curve=PowerCurve(
                                max_tension=41.2,
                                short_tension=50.10,
                                max_ampere=10.81,
                                short_ampere=11.40
                                ),
                        cell=Cell(row=6,col=24)
                        )
        ),
        'CS 375W':PvFactory(
                cost=Cost(190_448/1.19,Currency.CLP),
                technical_sheet=PvTechnicalSheet(
                        brand='Canadian Solar',
                        model='CS3L375MS',
                        power=375,
                        area=(104.8,176.5,Length.CM),
                        efficiency=20.3,
                        ref_url='https://www.tiendatecnored.cl/panel-solar-375w-canadian-solar.html',
                        specs_url='https://www.tiendatecnored.cl/media/wysiwyg/ficha-tecnica/4703157.pdf',
                        power_curve=PowerCurve(
                                max_tension=34.1,
                                short_tension=41,
                                max_ampere=10.94,
                                short_ampere=11.68
                                ),
                        cell=Cell(group=2)
                        )
        ),
}