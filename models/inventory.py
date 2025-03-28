"""main wrapper dependencies"""
from functools import reduce
import json
from math import log

from datetime import datetime
from typing import Any,  Literal


from dotenv import dotenv_values
import matplotlib.pyplot as plt
import numpy
import pandas as pd
from pandas import DataFrame
from docxtpl import DocxTemplate,RichText
from uuid import uuid1 # pylint: disable=no-name-in-module
# pylint: disable=no-member
# error
from pyxirr import irr, npv # pylint: disable=no-name-in-module
import requests # pylint: disable=no-member

from models.bucket import Bucket
from models.components import Component, Specs, Tech
from models.consumption import Consumption, Energetic, EnergyBill
from models.econometrics import Cost, Currency
from models.emission import Emission
from models.energy_storage import Battery, EnergyStorage,Regime
from models.generator import EnergyGenerator
from models.geometry import GeoPosition
from models.photovoltaic import Photovoltaic, PvFactory, PvInput
from models.weather import Weather
from models.weather import WeatherParam as W

# from models.photovoltaic import Photovoltaic

class Building:
    """
    Site configuration
    ~~~~
    >>> initializer
    ... geolocation
    ... name
    ... address
    ... city
    building config like geolocation, name and basics operations"""

    consumptions:dict[str,Consumption] ={}

    def __init__(self,
                geolocation:tuple[float,float,float|None],
                name:str,
                address:str,
                city:str):
        self.geolocation = GeoPosition(*geolocation)
        self.name=name
        self.address=address
        self.city=city

    def add_consumptions(
        self,
        energetic:Energetic=Energetic.ELI,
        client_id:str=None,
        measurer_id:str=None,
        contract_id:str='BT1A',
        cost_increment:float=0,
        description:str='main',
        consumption:list[EnergyBill]=None,
        ):
        '''defining energy bill, '''
        instance=Consumption(energetic,client_id,measurer_id,contract_id)
        instance.set_cost_increment(cost_increment)
        instance.set_bill(*consumption)
        self.consumptions[description] = instance

    def consumption_forecast(self,group:list[str])->DataFrame:
        """return sum of all consumption groups in this building"""

        container:DataFrame = self.consumptions[group[0]].forecast()
        if len(self.consumptions)>1:
            for it in group[1:]:
                calc = self.consumptions[it].forecast()
                container['energy'] = calc['energy'] + container['energy']
        return container


    def plot_consumption_forecast(self,group:list[str]):
        "generate graph"
        data:DataFrame = self.consumption_forecast(
            group=group)
        plotter = plt.subplot()
        plotter.plot(data['month'].values,data['energy'].values,linewidth=2.0)
        plotter.set_xlabel('mes')
        plotter.set_ylabel('kWh')
        plt.savefig("build/plot_consumption_forecast.png")

type Connection = Literal['hybrid','netbilling','ongrid','offgrid']


class Project:
    """
    Main Wrapper, globing all installs
    ~~~~
    ... building: @Building Class
    ... technology: @Tech Enum Class
    """
    components:dict[str,list[Component]] = {}
    generation_group_id:str = "generation"
    bucket:Bucket = Bucket()
    power_production:DataFrame|None = None # local storage energy daily generation
    _performance:DataFrame = DataFrame()

    def __init__(
        self,
        title:str,
        connection_type:Connection,
        building:Building,
        technology:list[Tech]|None = None,
        ) -> None:


        #building config
        self.emissions = Emission()
        self.technology = technology or [Tech.PHOTOVOLTAIC]
        self.building = building
        self.title:str = title + ' ' + self._connection_type_local(connection_type)
        self.connection_type=connection_type

        #weather env
        print('getting weather data...')
        self.weather = Weather(building.geolocation,\
            [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M])
        self.weather.get_data()

        #currency init
        self._load_exchanges()

    @property
    def connection_type_local(self)->str:
        """name in local spanish lang ES-cl"""
        return self._connection_type_local(self.connection_type)

    def _connection_type_local(self, connection_type:Connection)->str:
        match connection_type:
            case 'offgrid':
                return 'Off-grid'
            case 'netbilling':
                return 'Net-billing'
            case 'hybrid':
                return 'Híbrido'
            case 'ongrid':
                return 'Net-billing'
            case _:
                return ''


    def add_component(self,gloss:str,*components:Component,generator:bool=False):
        """
        Add component, in requires and identifier,
        """
        if generator:
            self.generation_group_id = gloss #defines generation "tag" need to be fix TODO:unappropriated implement

        if gloss in self.components:
            self.components[gloss].append(components)

        self.components[gloss] = list(components)

        self.bucket.add_item(gloss,*components)

    def add_generator(self,equipment:PvFactory,*generators:PvInput) -> None:
        """add energy generator component dedicate """
        eq = list(map(lambda it:equipment.factory(
            weather=self.weather,
            description=it.description,
            quantity=it.quantity,
            orientation=it.orientation),
            generators)
            )

        self.add_component('generación',*eq,generator=True)

    def add_storage(
        self,
        tag:str,
        hours_autonomy:int,
        regime:Regime,
        *extra_component:Component)->None:
        """auto config energy storage with default 250Ah GEL equipment"""

        if hours_autonomy == 0:
            return None

        self.add_component(
            tag,
            Battery(
                description='Baterías',
                specifications=Specs(
                    category='Storage',
                    brand='MaxPower',
                    model='MP GEL12-250',
                    ref_url='https://www.tiendatecnored.cl/bateria-gel-ciclo-profundo-12v-250ah.html',
                    specs_url='https://www.tiendatecnored.cl/media/wysiwyg/ficha-tecnica/4703148.pdf',
                    clase='Ciclo Profundo',
                    tipo='GEL'
                    ),
                cost_per_unit=Cost(305_990,Currency.CLP),
                volt=12,
                charge=250,
                demand=self.building.consumption_forecast(['main'])['energy'].to_list(),
                hours_autonomy=hours_autonomy,
                use_regime=regime,
            ),
            *extra_component
        )

    def has_storage(self)->bool:
        """check storage capability"""
        for _,group in self.components.items():
            for comp in group:
                if isinstance(comp,EnergyStorage):
                    return True
        return False




    def energy_production(self)->DataFrame|None:
        """extract and sum all energy generation component"""

        #check object local storage
        if self.power_production is not None:
            return self.power_production

        number_of_components:int  = len(self.components[self.generation_group_id])

        #check for generation component content
        if number_of_components == 0:
            raise ValueError('no component found')

        #check for Photovoltaic component
        for it in self.components[self.generation_group_id]:
            if not isinstance(it,EnergyGenerator):
                raise ValueError(f'{it}is not a energy gen component')

        #proceed for loop addition
        container:DataFrame = self.components[self.generation_group_id][0].get_energy().copy() #copy class fix overwriting object

        if number_of_components>1:
            for it in self.components[self.generation_group_id][1:]:

                aux_component:DataFrame = it.get_energy()
                container['System_capacity_KW'] += aux_component['System_capacity_KW']

                container['Temperature_cell'] = \
                    (container['Temperature_cell'] + aux_component['Temperature_cell'])/2

                container['IRR_incident'] = \
                    (container['IRR_incident'] + aux_component['IRR_incident'])/2

        #storage in local param
        self.power_production:DataFrame = container

        return container

    def production_array(self)->list[DataFrame]:
        "get energy production DataFrame PER generation unit module"
        return list(map(lambda unit:unit.get_energy(),self.components[self.generation_group_id]))

    def performance(self,
                    consumptions:list[str]=None,
                    connection:Connection = 'netbilling',):
        """generates monthly result for
        savings and netbilling performance"""

        production:DataFrame = self.energy_production()[["month","System_capacity_KW"]]\
            .groupby(["month"],as_index=False).sum()

        future:DataFrame = self.building.consumption_forecast(
            group=consumptions if consumptions else ['main'],
            )

        res = future.merge(right=production,how='left')
        res = res.rename(columns={'energy':'consumption','System_capacity_KW':'generation'})

        match connection:
            case 'netbilling':#energy sell to net
                #when energy generation is bigger than consumption return delta, else 0
                res['netbilling'] = numpy.where(
                    res['generation']>=res['consumption'],
                    res['generation']-res['consumption'],
                    0
                    )

                res['savings'] = numpy.where(
                    res['generation']>=res['consumption'],
                    res['consumption'],
                    res['generation']
                    )

            case 'ongrid': #not netbilling
                res['netbilling'] = numpy.where(
                    res['generation']>=res['consumption'],
                    0,
                    0
                    )

                res['savings'] = numpy.where(
                    res['generation']>=res['consumption'],
                    res['consumption'],
                    res['generation']
                    )

            case 'offgrid':#only battery saving
                res['netbilling'] = numpy.where(
                    res['generation']>=res['consumption'],
                    0,
                    0
                    )

                res['savings'] = numpy.where(
                    res['generation']>=res['consumption'],
                    res['generation'],
                    res['generation']
                    )
        #emissions
        res['benefits'] = res['savings']*res['unit_cost']#"+res['netbilling']*res['unit_cost']
        res['netbilling_income'] = res['netbilling']*res['unit_cost']*(1-0.07)#"+res['netbilling']*res['unit_cost']


        eva_period = datetime.now().year +1
        res['CO2 kg'] = res['generation']*self.emissions.annual_projection(eva_period)

        #local storage
        self._performance = res

        return res

    @property
    def nominal_power(self)->tuple[float,list[float]]:
        "system capacity in kW"
        components:list[Component|Photovoltaic]  = self.components[self.generation_group_id]

        if len(components)==0:
            raise ValueError('no component found')

        for it in components:
            if not isinstance(it,Photovoltaic):
                raise ValueError('no energy component found')

        power_list:list[float] = [fv.nominal_power() for fv in components]
        redux:float = 0.0
        for it in power_list:
            redux+= it

        return (redux,power_list)

    @property
    def n_generator(self)->int:
        """number of generation units"""
        gen:list[Photovoltaic] = self.components['generación']
        return sum(list(map(lambda it: it.quantity,gen)))


    @property
    def area(self)->float:
        "return total area used by this project"
        area =0
        for it in self.components[self.generation_group_id]:
            comp:Photovoltaic = it
            area += comp.area

        return float(f'{area:.2f}')

    def economical_analysis(self,currency:Currency,n_years:int=10,rate:float = 6/100,fmt=False):
        """"VAN TIR flux financial analysis"""

        investment = self.bucket.total().value
        income_by_saving:float = self._performance['benefits'].sum()
        income_by_netbilling:float = self._performance['netbilling_income'].sum()
        ratio = self.building.consumptions['main'].get_cost_increment

        flux_by_saving = [0,*[float(income_by_saving*(ratio**period)) for period in range(n_years)]]
        flux_by_netbilling = [0,*[float(income_by_netbilling*(ratio**period)) for period in range(n_years)]]
        flux_by_inv= [-investment,*[0]*n_years]

        flux:list[float] = [flux_by_saving[i]+flux_by_netbilling[i]+flux_by_inv[i] for i in range(len(flux_by_saving))]
        flux_acc:list[float]=[]

        flux_acc:list[float] = [] #project sum flux
        for i,period in enumerate(flux):
            if i == 0:
                flux_acc.append(period)
                continue

            flux_acc.append(flux_acc[i-1]+period)

        res_npv = npv(rate,flux)
        res_irr = irr(flux)
        res_sri = self._ir(rate_cost=rate,flux=flux,method='exact')

        if fmt:
            return {'rate':f'{rate*100:.1f}%',
                'investment':f'${investment:,.2f} . -',
                'years':n_years,
                'flux':DataFrame({'flux':flux,'accumulated':flux_acc}).round(0),
                'currency':currency.value,
                'npv':f'$ {res_npv:,.0f}. -',
                'irr':f'{res_irr*100:.2f} %',
                'return':f'{res_sri:.2f}',
                }

        return {'rate':rate,
                'inverts':investment,
                'years':n_years,
                'flux_by_savings':flux_by_saving,
                'flux_by_netbilling':flux_by_netbilling,
                'flux':flux,
                'accumulated':flux_acc,
                'currency':currency.value,
                'npv':res_npv,
                'irr':res_irr,
                'return':res_sri,
                'npv_bool':res_npv>0,
                'irr_bool':res_irr>0.05,
                }
    def storage(self)->dict[str,float]|None:
        """storage capacity
        >>>result
        ...None: no storage system,
        ...Obj : main highlights
        """
        container:list[Battery] = []

        for _,component_group in self.components.items():
            for component in component_group:
                if isinstance(component,Battery):
                    container.append(component)

        if len(container) == 0:
            return None

        aux = {
            "specification":list(map(lambda it:f'{it.specification:a}',container)),
            "wh_per_module":reduce(lambda acc,it:acc+it,[it.storage for it in container]),
            "hours_autonomy":reduce(lambda acc,it:acc+it,[it.hours_autonomy for it in container]),
            "units":reduce(lambda acc,it:acc+it,[it.quantity for it in container]),
            "hourly_avg_demand":reduce(lambda acc,it:acc+it,[it.hourly_avg_demand for it in container]),
        }

        return {
            "specification":aux['specification'],
            "energy_storage_kwh":f'{aux['wh_per_module']*aux['units']/1000:.2f}',
            "hours_autonomy":aux['hours_autonomy'],
            "units":aux['units'],
            "avg_demand_per_hour":f'{aux['hourly_avg_demand']:.2f} kWh',
        }

    def context(self,template:DocxTemplate|None)->dict[str,Any]:
        #cspell: disable
        "return object with information for generate DOCX template"
        #aux
        gmaps = RichText()
        if template is not None:
            gmaps.add('ver maps',
                    url_id=template.build_url_id(self.weather.geo_position.gmaps),
                    bold=True,
                    underline=True)
        #demand projection
        forecast:DataFrame = self.building.consumptions['main'].forecast()
        base:DataFrame= self.building.consumptions['main'].to_dataframe()

        #production
        performance  = self.performance(
            consumptions=['main']
            )
        production_performance = performance[['month','consumption','generation','netbilling','savings']]
        #system capacity
        production_array = list(
            map(lambda it:f'{it['System_capacity_KW'].sum():.2f} kWh',
                self.production_array()))


        ctx:dict[str,any] = {
            #report
            "report_date":datetime.now().strftime("%a, %d de %B %Y"),
            "report_version":"ver."+str(uuid1()).split('-',maxsplit=1)[0],
            #site
            "project":self,
            "gmaps":gmaps,

            #about this project
            "project_type" : self.technology[0].value.capitalize(),
            "project_size":f"{self.nominal_power[0]:.2f} kW",
            "total_cost": f"{self.bucket.total():net.CLP}",
            #benefits
            "annual_benefits": f"CLP$ {performance['benefits'].sum():,.0f}",
            "energy_production": f"{performance['generation'].sum():.0f} kWh/año",
            "energy_netbilling": f"{performance['netbilling'].sum():.0f} kWh/año",
            "energy_savings": f"{performance['savings'].sum():.0f} kWh/año",
            #emissions
            "emission_reduction":f"{performance['CO2 kg'].sum():,.2f} kg CO2",
            "emission_forecast":f'{self.emissions.annual_projection(2024):.4f} Ton CO2/MWh',
            "table_emission_historic":self.emissions
            .annual_avg().round(4)
            .to_markdown(index=False),
            "table_emission_reduction":performance[['month','CO2 kg']]
            .round(2).rename(columns={'month':'mes'})
            .to_markdown(index=False),

            #consumptions
                ##base
            "table_base_consumptions":base.to_markdown(index=False),
                ##projected or future
            "cost_increment":f"{self.building.consumptions['main'].get_cost_increment*100-100:.2f} %",
            "forecast_consumption":f"{forecast['energy'].sum()} kWh/año",
            "table_forecast_consumptions":
                forecast.rename(columns={
                        "energy": "proyectado kWh",
                        "month":'mes',
                        'unit_cost':'costo $CLP/kWh'
                        }).to_markdown(index=False,floatfmt=',.2f'),
            #components
            "table_components":self.bucket.bucket_df(lambda it:{
                'descripción':it.description,
                'cantidad':it.quantity,
                'costo':it.cost.net(Currency.CLP)[0]})
            .to_markdown(index=True,floatfmt=',.0f'),

            "table_energy_components":self.bucket.gx_bucket_df()\
                [['glosa','descripción','cantidad','global']]
                    .to_markdown(index=True),
            #production
            "table_production_array":production_array,
            "table_production_performance":production_performance
                    .rename(columns={
                            'month':'mes',
                            'consumption':'demanda',
                            'generation':'generación',
                            'savings':'ahorro',
                            }).round(2).to_markdown(index=False),
            #economics
            "eco":self.economical_analysis(Currency.CLP,fmt=True),
            "eco_num":self.economical_analysis(Currency.CLP,fmt=False),
            #energy storage unit
            "storage_existance":True if self.storage() else False,
            "storage_capacity":self.storage(),

        }
        return ctx

    def _load_exchanges(self):
        #env values
        config = dotenv_values(".env.local")
        print('getting currencies data...')
        # national units https://mindicador.cl/api
        query_factor:requests.Response = requests.get('https://mindicador.cl/api',timeout=1000)
        ratios_cl = json.loads(query_factor.text)
        usd_clp:float = ratios_cl['dolar']['valor']
        Cost.set_exchange(Currency.CLP,usd_clp)
        Cost.set_exchange(Currency.UF,usd_clp/ratios_cl['uf']['valor']) # 1 dolar in UF
        Cost.set_exchange(Currency.UTM,usd_clp/ratios_cl['utm']['valor']) # 1 dolar in Utm

        # exchange rates https://app.freecurrencyapi.com/dashboard
        query_exchange:requests.Response = requests.get(config["CURRENCY_API_KEY"],timeout=1000)

        currency_ratios = json.loads(query_exchange.text)
        Cost.set_exchange(Currency.EUR,currency_ratios['data']['EUR'])
        Cost.set_exchange(Currency.GBP,currency_ratios['data']['GBP'])
        Cost.set_exchange(Currency.BRL,currency_ratios['data']['BRL'])

    def _ir(self,rate_cost:float,flux:list[float],method:Literal['simple','exact']='simple')-> float:
        i = -flux[0]
        b = flux[1]

        if method == 'simple': #simple Inverstment Time Return
            return i/b

        if rate_cost == 0: #return simple ITR
            return i/b

        #find period when is positive flux
        if method == 'exact':
            return log((i*rate_cost/b)+1)/log(rate_cost+1)

        return 0