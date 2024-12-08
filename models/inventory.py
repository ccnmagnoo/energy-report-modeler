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
from uuid import uuid1
# pylint: disable=no-member
# error
from pyxirr import irr, npv # pylint: disable=no-name-in-module
import requests # pylint: disable=no-member

from models.components import Component, Tech
from models.consumption import Consumption, ElectricityBill, Energetic, EnergyBill
from models.econometrics import Cost, Currency
from models.emission import Emission
from models.energy_storage import Battery
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
        description:str,
        energetic:Energetic,
        cost_increment:float,
        consumption:list[EnergyBill],

        ):
        '''defining energy bill, '''
        instance=Consumption(energetic)
        instance.set_cost_increment(cost_increment)
        instance.set_bill(consumption)
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

type Connection = Literal['netbilling','ongrid','offgrid']


class Project:
    """
    Main Wrapper, globing all installs
    ~~~~
    ... building: @Building Class
    ... technology: @Tech Enum Class
    """
    components:dict[str,list[Component]] = {}
    power_production:DataFrame|None = None # local storage energy daily generation
    generation_group:str|None = None
    _performance:DataFrame = DataFrame()

    def __init__(
        self,
        title:str,
        building:Building,
        technology:list[Tech]|None = None,
        consumption:dict[str,Any]|None=None
        ) -> None:


        #building config
        self.emissions = Emission()
        self.technology = technology or [Tech.PHOTOVOLTAIC]
        self.building = building
        self.title:str = title
        self.bucket:dict[str,float|DataFrame]={}

        #weather env
        print('getting weather data...')
        self.weather = Weather(building.geolocation,\
            [W.TEMPERATURE,W.DIRECT,W.DIFFUSE,W.ALBEDO,W.ZENITH,W.WIND_SPEED_10M])
        self.weather.get_data()

        #currency init
        self._load_exchanges()

        #consumptions
        print('adding consumptions data...')
        model:type[EnergyBill] = None
        match consumption['energetic']:
            case Energetic.ELI:
                model = ElectricityBill

        self.building.add_consumptions(
            description=consumption['description'],
            energetic=consumption['energetic'],
            cost_increment=consumption['cost_increment'],
            consumption= [model(it[0],it[1],it[2]) for it in consumption['consumption']]
        )

    def add_component(self,item:str,*args:Component|Photovoltaic,generator:bool=False):
        """
        Add component, in requires and identifier,
        """
        if generator:
            self.generation_group = item

        if item in self.components:
            self.components[item].append(args)

        self.components[item] = list(args)

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


    def energy_production(self)->DataFrame|None:
        """extract and sum all energy generation component"""

        #check object local storage
        if self.power_production is not None:
            return self.power_production

        number_of_components  = len(self.components[self.generation_group])

        #check for generation component content
        if number_of_components == 0:
            raise ValueError('no component found')

        #check for Photovoltaic component
        for it in self.components[self.generation_group]:
            if not isinstance(it,Photovoltaic):
                raise ValueError(f'{it}is not a energy gen component')

        #proceed for loop addition

        container:DataFrame = self.components[self.generation_group][0].get_energy().copy() #copy class fix overwriting object

        if number_of_components>1:
            for it in self.components[self.generation_group][1:]:

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
        return list(map(lambda unit:unit.get_energy(),self.components[self.generation_group]))

    def performance(self,
                    consumptions:list[str],
                    connection:Connection = 'netbilling',):
        """generates monthly result for
        savings and netbilling performance"""

        production:DataFrame = self.energy_production()[["month","System_capacity_KW"]]\
            .groupby(["month"],as_index=False).sum()

        future:DataFrame = self.building.consumption_forecast(
            group=consumptions,
            )

        res = future.merge(right=production,how='left')
        res = res.rename(columns={'energy':'consumption','System_capacity_KW':'generation'})

        match connection:
            case 'netbilling':
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
            case 'ongrid':
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
            case 'offgrid':
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
        res['benefits'] = res['savings']*res['unit_cost']
        eva_period = datetime.now().year +1
        res['CO2 kg'] = res['generation']*self.emissions.annual_projection(eva_period)

        #local storage
        self._performance = res

        return res

    @property
    def nominal_power(self)->tuple[float,list[float]]:
        "system capacity in kW"
        components:list[Component|Photovoltaic]  = self.components[self.generation_group]

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
        for it in self.components[self.generation_group]:
            comp:Photovoltaic = it
            area += comp.area

        return float(f'{area:.2f}')

    def bucket_list(self,currency:Currency|None,**overloads:float)->dict[str,DataFrame|float]:
        "get all cost related by components"

        #generate bucket
        container:list[tuple[str,str,int,float,str]] = []
        bucket_cost:float = 0
        #write gloss
        for gloss,item in self.components.items():
            for component in item:

                value,curr = component.total_cost_before_tax(currency)
                
                #auxiliary object
                obj_item = {
                    'gloss':gloss,
                    'description':component.description,
                    'details':component.specification,
                    'quantity':component.quantity,
                    'cost':value,
                    'currency':curr.name
                }
                container.append(obj_item)
                
        #build dataframe
        
        #sub-total normalice in clp
        for gloss,item in self.components.items():
            for component in item:
                bucket_cost+=component.total_cost_before_tax(currency=Currency.CLP)[0]

        bucket_cost=round(bucket_cost,0)

        #define subtotal
        res = {
            'bucket':pd.DataFrame.from_dict(container),
            'sub-total':bucket_cost,
            }
        
        #charge overloads
        for it in overloads.items():
            if it[1]>1 and it[1]<100:
                res[f'{it[0]} ({it[1]}%)'] = round(bucket_cost*it[1]/100,0)
            else:
                raise ValueError('overloads has to be between 1-100')

        #sum float items
        acc:float=0 #add final total
        for _,cost in res.items():
            if isinstance(cost,float):
                acc+=cost
        #compose
        res = {
            **res,
            'total net':acc,
            'Imp(19%)':round(acc*.19,0),
            'total':round(acc*1.19,0),
            }
        
        self.bucket:dict[str,float|DataFrame] = res

        return res

    def economical_analysis(self,currency:Currency,n_years:int=10,rate:float = 6/100,fmt=False):
        """"VAN TIR flux financial analysis"""
        investment = self.bucket['total']
        first_period_income:float = self._performance['benefits'].sum()
        flux:list[float] = [-investment,first_period_income]

        for period in range(2,n_years+1):#project benefits in n years
            last_period = flux[period-1]
            flux.append(last_period*(self.building.consumptions['main'].get_cost_increment))

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
            "specification":list(map(lambda it:it.specification,container)),
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
        forecast:DataFrame = self.building.consumptions['main'].forecast(cost_increment=5/100)
        base = pd.DataFrame.from_dict(self.building.consumptions['main'].base())
        #production
        performance  = self.performance(
            consumptions=['main']
            )
        production_performance = performance[['month','consumption','generation','netbilling','savings']]
        #system capacity
        production_array = list(
            map(lambda it:f'{it['System_capacity_KW'].sum():.2f} kWh',
                self.production_array()))

        bucket_df:DataFrame = self.bucket['bucket']

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
            "total_cost": f"CLP$ {self.bucket["total"]:,.0f}",
            #benefits
            "annual_benefits": f"CLP$ {performance['benefits'].sum():,.0f}",
            "energy_production": f"{performance['generation'].sum():.0f} kWh/año",
            "energy_netbilling": f"{performance['netbilling'].sum():.0f} kWh/año",
            "energy_savings": f"{performance['savings'].sum():.0f} kWh/año",
            #emissions
            "emission_reduction":f"{performance['CO2 kg'].sum():,.2f} kg CO2",
            "emission_forecast":f'{self.emissions.annual_projection(2024):.4f} Ton CO2/MWh',
            "table_emission_historic":self.emissions.annual_avg().round(4).to_markdown(index=False),
            "table_emission_reduction":performance[['month','CO2 kg']].round(2).rename(columns={'month':'mes'}).to_markdown(index=False),

            #consumptions
                ##base
            "table_base_consumptions":
                base.rename(columns={
                        "energy": "proyectado kWh",
                        "month":'mes',
                        'unit_cost':'costo $CLP/kWh'
                        }).to_markdown(index=False),
                ##projected or future
            "cost_increment":f"{self.building.consumptions['main'].get_cost_increment*100-100:.2f} %",
            "forecast_consumption":f"{forecast['energy'].sum()} kWh/año",
            "table_forecast_consumptions":
                forecast.rename(columns={
                        "energy": "proyectado kWh",
                        "month":'mes',
                        'unit_cost':'costo $CLP/kWh'
                        }).to_markdown(index=False),
            #components
            "table_components":bucket_df
                    [['description','quantity','cost']]
                    .rename(columns={
                        'description':'descripción',
                        'quantity':'cantidad',
                        'cost':'valor'
                    })
                    .to_markdown(index=True,floatfmt=',.0f'),
        
            "table_energy_components":bucket_df[bucket_df['gloss']=='generación']\
                [['description','details','quantity']]
                    .rename(columns={
                                'description':'descripción',
                                'details':'detalle',
                                'quantity':'cantidad'
                    })
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