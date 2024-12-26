from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Callable, Literal, Self
import numpy as np
from sklearn.linear_model import LinearRegression

import pandas as pd
from pandas import DataFrame
from models.econometrics import Cost, Currency

class Energetic(Enum):
    '''
    Energy source type
    ~~~~
    calorific power inferior :
    ...(source)[https://ingemecanica.com/utilidades/objetos/tablas/calorifico/calor49.jpg]

    '''
    ELI = 'electricidad'
    GLP = 'gas licuado'
    GNL = 'gas natural licuado'
    GN = 'gas natural cañería'
    DIESEL = 'diesel oil'
    WOOD = 'leña'
    CARBON = 'carbón'
    D95 = '95 octanos'

class Unit(Enum):
    '''Physical unit specification'''
    KG = 'kg'
    M3 = 'm³'
    KWH = 'kWh'
    M = 'm'
    LT = 'lt'

class Supply(Enum):
    """
    ### Energy supply mode,
    > - STORE : distribution by reserves, diesel
    > - DEMAND : distribution on-demand, electricity
    """
    STORAGE = "storage"
    DEMAND = "on-demand"
@dataclass
class Property:
    """
    Fuel Chemical properties
    """
    kwh_per_kg:float # kWh/unit
    kg_per_m3:float # kg/m3
    unit:Unit # billing unit measure kg,m3,...
    supply:Supply

    def energy_equivalent(self,quantity:float=0,measure_unit:Unit = Unit.KG)->float:
        """returning kWh equivalent energy"""
        if measure_unit == Unit.LT:
            return self.kwh_per_kg*quantity*1000/self.kg_per_m3

        return self.kwh_per_kg*quantity

properties:dict[Energetic,Property] = {
    Energetic.ELI: Property(kwh_per_kg=1,kg_per_m3=1,unit=Unit.KWH,supply=Supply.DEMAND),
    Energetic.GNL: Property(kwh_per_kg=12.53,kg_per_m3=341,unit=Unit.KG,supply=Supply.STORAGE),
    Energetic.DIESEL: Property(kwh_per_kg=11.82,kg_per_m3=850,unit=Unit.KG,supply=Supply.STORAGE),
    Energetic.GLP:Property(kwh_per_kg=12.69, kg_per_m3=350,unit=Unit.KG,supply=Supply.STORAGE),
    Energetic.GN: Property(kwh_per_kg=40.474,kg_per_m3=0.737, unit=Unit.M3,supply=Supply.DEMAND)
            }



class EnergyBill(ABC):
    """
    Energy consumption Item
    >>>inputs
    date_billing = str format DD-MM-YYYY
    """
    def __init__(self,
                date_billing:str,
                consumption:float, # in natural units
                energetic:Energetic,
                cost:float,
                currency:Currency=Currency.CLP
                ) -> None:
        self.energetic = energetic
        self.property:Property = properties[energetic]
        self.energy = properties[energetic].energy_equivalent(consumption)  # in equivalent kWh
        self.cost = Cost(cost,currency)
        self.date_billing = self.str_to_date(date_billing)

    def unitary_cost(self)->float:
        """unitary cost in $curr/kWh equivalent, default currency"""
        return self.cost.gross(None)[0]/self.energy

    @staticmethod
    def str_to_date(date_str:str)->datetime.datetime:
        """ dd-mm-yyy string to datetime"""
        s = date_str.split("-",maxsplit=3)
        s = [int(cal) for cal in s]
        s.reverse()
        return datetime.datetime(*s)


    @abstractmethod
    def to_dict(self,adapter:Callable[[Self],dict])->dict:
        """return all properties stores as a dict"""

class Tension(Enum):
    """level of tension AT:400v o BT:220v"""
    AT='AT'
    BT='BT'
type ITension = Literal['AT','BT']


class Contract(Enum):
    """type of contract"""
    _1A = '1A'
    _1B = '1B'
    _2 = '2'
    _3 = '3'
    _41 = '4.1'
    _42 = '4.2'
    _43 = '4.3'
type IContract = Literal['_A1','_B1','_2','_3','_41','_42','_43']

class RushHour(Enum):
    """rush hours config"""
    PP = 'PP'
    PPP = 'PPP'
    NA = ''
type IRushHour = Literal['NA','PP','PPP']

class Fare:
    '''
    Fare electric billing :default BT1A
    '''
    def __init__(self,
                tension:Tension = Tension.BT,
                contract:Contract = Contract._1A,
                rush_hour:RushHour = RushHour.NA
                ) -> None:
        self.tension = tension
        self.contract = contract
        self.rush_hour = rush_hour

    def get_fare(self)->str:
        '''return properly compose fare'''
        return self.tension.value +'-'+ self.contract.value +((' '+self.rush_hour.value) if self.rush_hour.value != '' else '')

    def __str__(self)->str:
        return self.get_fare()

class ElectricityBill(EnergyBill):
    '''Electricity billing details consumption'''
    def __init__(self,
                lecture_start: str,
                lecture_end: str,
                energy_consumption:float,
                energy_cost:float = 0,
                currency:Currency = Currency.CLP,
                fare:tuple[ITension,IContract,IRushHour] = ('BT','_1A','NA'),
                **props:float
                ) -> None:
        super().__init__(lecture_end,energy_consumption, Energetic.ELI, energy_cost,currency)

        self.lecture_star = self.str_to_date(lecture_start)
        self.energy_unit:Unit = Unit.KWH
        self.fare = Fare(
            tension=Tension[fare[0]],
            contract=Contract[fare[1]],
            rush_hour=RushHour[fare[2]]
            )
        self.props = props

    @staticmethod
    def _default_adapter(it:Self)->dict:
        i:ElectricityBill = it

        return {
            "tarifa":str(i.fare),
            "lectura":str(i.date_billing),
            "consumo":f'{i.energy} {i.energy_unit.value}',
            **i.props,
            "unitario":f'{i.cost.value/i.energy:.2f} {i.cost.currency.name}/{i.energy_unit.value}',
            "total":f"{i.cost:net.CLP}",
        }

    def to_dict(self,
                adapter:Callable[[Self],dict]=None)->dict:
        adapter_cfg = adapter if adapter else self._default_adapter
        return adapter_cfg(self)


class Consumption:
    """global energy billing and estimate  projection in 12 month"""

    _records:list[EnergyBill]=[]
    _cost_increment_rate:float=1
    _index=0

    def __init__(
        self,
        energetic:Energetic,
        client_id:str=None,
        measurer_id:str=None,
        contract_id:str=None,
        ) -> None:
        self.energetic = energetic
        self.property = properties[energetic]
        self.client_id:str=client_id,
        self.measurer_id:str=measurer_id,
        self.contract_id:str=contract_id,

    def set_bill(self,*billing:EnergyBill)->None:
        """set list o single billing"""
        self._records = [*self._records,*billing]
        #acs sorting by date
        self._records.sort(key=lambda bill:bill.date_billing)

    def set_cost_increment(self,percentage:float=0):
        """set cost increment factor"""
        if percentage >= 0 and percentage<=100:
            self._cost_increment_rate = (percentage/100)+1
        else:
            raise ValueError('cost increment value must be between 0 an 100')

    @property
    def get_cost_increment(self)->float:
        """return float -1 of cost increment"""
        return self._cost_increment_rate

    def to_list(self)->list[dict]:
        """return a list of consumptions value"""

        return list(
            map(lambda bill:{"date":bill.date_billing,"energy":bill.energy},
            self._records)
            )
    @property
    def total_consumption(self)->tuple[float,str]:
        """return total sum"""
        return sum(list(map(lambda it:it.energy,self._records))),"kWh"

    def __iter__(self):
        return self

    def __next__(self)->EnergyBill:
        if self._index < len(self._records):
            res = self._records[self._index]
            self._index+=1
            return res
        else:
            self._index=0
            raise StopIteration

    def to_dataframe(self)->DataFrame:
        """consumption billing in DataFrame format"""
        return DataFrame.from_dict(list(map(lambda it:it.to_dict(),self._records)))

    def base(self)->list[dict[str,int]]:
        """generate energy consumption base
            without completion or any approximation
        """
        base  = [{"month":period,"lecture":0,"energy":0,"unit_cost":0,"total":0} for period in range(1,13)]

        for bill in self._records:
            #load consumptions
            bill_month = bill.date_billing.month
            base[bill_month-1]["energy"]=base[bill_month-1]["energy"]+bill.energy
            base[bill_month-1]["lecture"]=bill.date_billing.strftime(format="%d-%m-%Y")
            base[bill_month-1]["unit_cost"]=bill.unitary_cost()
            base[bill_month-1]["total"]=str(bill.cost)

        return base

    def forecast(self,
                            method:Callable[[float,float],float]=lambda a,b:(a+b)/2,
                            )->DataFrame:
        """estimate monthly energy consumption from the next year
        >>>>completion: forecast has an estimated consumption
        for a period of time divided by month
        completion defines how many month has to be completed,
        between  Zero (default: without changes) and 12, por each month projection.
        """
        data:list[dict[str,float]] = []
        if self.property.supply == Supply.DEMAND:
            data = self._interpolate(method)

        if self.property.supply == Supply.STORAGE:
            data =  self._distribute()

        df = pd.DataFrame.from_dict(data)
        df = self._calc_cost_increment(
            data=df,
            weight= self._cost_increment_rate)
        
        df.total = df.unit_cost*df.energy

        return df[['month','unit_cost','energy','total']]

    def _calc_cost_increment(self,data:DataFrame,weight:float=1.0)->pd.DataFrame:
        """estimate cost incremental by unitary volume clp/kWh
        >>>includes
        ...weight*cost multiplier
        """
        curve = self.base()
        lg = LinearRegression()
        lg.fit(
            X=np.array([it['energy'] for it in curve if it['energy']>0]).reshape(-1,1),
            y=np.array([it['unit_cost'] for it in curve if it['unit_cost']>0]).reshape(-1,1),
            )

        data['unit_cost'] = data['energy'].apply(lambda it: lg.predict([[it]])[0][0]*weight)

        return data


    def _interpolate(self,method:Callable[[float,float],float])-> list[dict[str,float]]:
        """consume interpolation, for fill the gaps """
        base = self.base()
        forecast = [*base]
        cycle =[*base,*base,*base] #[{"month":1,"energy":100}]
        paginate:int = 12

            # by distribution on-demand like electricity and natural gas.
        for idx,it in enumerate(forecast):
            if it["energy"]==0.0:                #find left, right and distance
                ## find left not 0
                left = [i["energy"] for i in cycle[:paginate+idx] if i['energy']>0] # all previous non zero energy month
                ## find right not 0
                right = [i["energy"] for i in cycle[paginate+idx:] if i['energy']>0]# all next non zero energy month
                print(f"boundaries in month {it["month"]} :",left[-1],"<->",right[0])
                it['energy'] = method(left[-1],right[0])
                
        return forecast

    def _distribute(self)-> list[dict[str,float]]:
        """consume distribution, considering storing between charges"""
        base = self.base()
        forecast = [*base]
        cycle =[*base,*base,*base] #[{"month":1,"energy":100}]
        SPREAD:int = 12

        def counter(temporal:list[dict[str,float]])->int:
            tmp = [*temporal]
            tmp.reverse()
            dist_temporal:int = 0
            for it in tmp:
                if it["energy"] == 0:
                    dist_temporal+=1
                else:
                    break
            return dist_temporal

        for idx, it in enumerate(base):
            reserve:float = 0
            print('check period: ',it)
            if it["energy"] > 0:
                #recharge period
                reserve = it['energy']
                # count previous uncharged period on cycle
                dist_cycle = counter(cycle[:idx+SPREAD])
                split_by = dist_cycle+1
                ## in-period size
                dist_period = counter(base[:idx])
                ## redistribution on current period
                dist_energy = reserve/(split_by) #kwh/month
                #redistribution
                print(f"redistribution in month {it["month"]}:",f"{dist_energy} kWh in ",f"{dist_period} months ","divided by:",split_by)
                for i in range(idx-dist_period,idx+1):
                    forecast[i]["energy"] = dist_energy
        return forecast

# End-of-file (EOF)