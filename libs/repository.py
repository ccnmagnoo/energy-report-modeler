from models.components import Component
from models.econometrics import Cost, Currency

#cspell: disable
repo = {
    'inverter':{
        '3W_mono':Component('Inversor on-grid',
                model='Voltronic 3kW 48V',
                reference='https://www.tiendatecnored.cl/inversor-string-canadian-solar-3kw.html',
                specification='Ongrid 3kW Monofásico',
                cost_per_unit=Cost(511290,Currency.CLP)),
        '5kW_mono':Component('Inversor Híbrido',
                model='Voltronic 5kW 48V',
                reference='https://solarbex.com/comprar/inversor-hibrido-5kw-48v-axpert/',
                specification='Híbrido 5kW Monofásico',
                cost_per_unit=Cost(869,Currency.EUR)),
        '7kW_mono':Component('Inversor Híbrido',
        model='Voltronic 7kW 48V',
        reference='https://solarbex.com/comprar/inversor-hibrido-7kw-48v-voltronic/',
        specification='Híbrido 7kW Monofásico',
        cost_per_unit=Cost(1255,Currency.EUR)),
        '12kW_3f':Component('Inversor Híbrido Trifásico',
        model='Deye Sun 12kW 380V',
        reference='https://solarbex.com/comprar/inversor-hibrido-deye-12kw-trifasico/',
        specification='Híbrido 12kW Trifásico',
        cost_per_unit=Cost(3190,Currency.EUR)),
    },
}