from abc import ABC
from dataclasses import dataclass
import datetime
from enum import Enum
from collections.abc import Callable
import numpy as np
from sklearn.linear_model import LinearRegression

import pandas as pd

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
    GNL = 'gas natural licuado',
    GN = 'gas natural cañería',
    DIESEL = 'diesel oil'
    WOOD = 'leña'
    CARBON = 'carbón'
    D95 = '95 octanos'

class Unit(Enum):
    '''Physical unit specification'''
    KG = 'kg',
    M3 = 'm³',
    KWH = 'kWh',
    M = 'm',
    LT = 'lt'

class Supply(Enum):
    """
    ### Energy supply mode,
    > - STORE : distribution by reserves, diesel
    > - DEMAND : distribution on-demand, electricity
    """
    STORAGE = "storage",
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
        #date from string
        datestr = date_billing.split("-",maxsplit=3)
        datestr = [int(cal) for cal in datestr]
        datestr.reverse()
        self.date_billing = datetime.datetime(*datestr)

    def unitary_cost(self)->float:
        """unitary cost in $curr/kWh equivalent, default currency"""
        return self.cost.cost_after_tax(None)[0]/self.energy


class FareTension(Enum):
    '''fare type'''
    AT='AT',
    BT='BT'

class FareType(Enum):
    '''
    Fare contract model
    '''
    A1 = '1A',
    B1 = '1B',
    T2 = '2',
    T3 = '3PP',
    T41 = '4.1',
    T42 = '4.2',
    T43 = '4.3'

class FareSubType(Enum):
    '''
    Fare contract model
    '''
    PP = 'PP',
    PPP = 'PPP'

class Fare:
    '''
    Fare electric billing :default BT1A
    '''
    def __init__(self,
                tension:FareTension = FareTension.BT,
                contract:FareType = FareType.A1,
                sub_type:FareSubType|None = None
                ) -> None:
        self.tension = tension,
        self.contract = contract,
        self.sub_type = sub_type

    def get_fare(self)->str:
        '''return properly compose fare'''
        return self.tension + self.contract + self.sub_type

class ElectricityBill(EnergyBill):
    '''Electricity billing details consumption'''
    def __init__(self,
                consumption:float,
                date_billing: str,
                cost:float = 0,
                currency:Currency = Currency.CLP,
                fare:Fare = Fare()
                ) -> None:
        super().__init__(date_billing,consumption, Energetic.ELI, cost,currency)
        self.energy_unit:Unit = Unit.KWH
        self.fare = fare

class Consumption:
    """global energy billing and estimate  projection in 12 month"""
    bucket:list[EnergyBill]=[]
    def __init__(self,energetic:Energetic) -> None:
        self.energetic = energetic
        self.property = properties[energetic]

    def set_bill(self,billing:list[EnergyBill]|EnergyBill)->None:
        """set list o single billing"""
        if isinstance(billing,list):
            # when is a bulk of bills 📄📄📄
            if len(self.bucket) > 0:
                self.bucket = [*self.bucket,*billing]
            else:
                self.bucket = billing
        else:
            # when just a one bill 📄
            if len(self.bucket) > 0:
                self.bucket = [*self.bucket,billing]
            else:
                self.bucket = [billing] # inventory (\r\n)
        #acs sorting by date
        self.bucket.sort(key=lambda bill:bill.date_billing)

    def records(self)->dict:
        """return a list of consumptions value"""

        return list(
            map(lambda bill:{"date":bill.date_billing,"energy":bill.energy},
            self.bucket)
            )

    def base(self)->list[dict[str,int]]:
        """generate energy consumption base
            without completion or any approximation
        """
        base  = [{"month":period,"energy":0,"unit_cost":0} for period in range(1,13)]

        for bill in self.bucket:
            #load consumptions
            bill_month = bill.date_billing.month
            base[bill_month-1]["energy"]=base[bill_month-1]["energy"]+bill.energy
            base[bill_month-1]["unit_cost"]=bill.unitary_cost()

        return base

    def forecast(self,
                            method:Callable[[float,float],float]=lambda a,b:(a+b)/2,
                            cost_increment:float=0.0
                            )->list[dict[str,float]]:
        """estimate monthly energy consumption from the next year
        >>>>completion: forecast has an estimated consumption
        for a period of time divided by month
        completion defines how many month has to be completed,
        between  Zero (default: without changes) and 12, por each month projection.
        """
        data:list = None
        if self.property.supply == Supply.DEMAND:
            data = self._interpolate(method)

        if self.property.supply == Supply.STORAGE:
            data =  self._distribute()
        df = pd.DataFrame.from_dict(data)
        df = self._cost_increment(data=df,weight=(1+cost_increment))    

        return df

    def _cost_increment(self,data:pd.DataFrame,weight:float=1.0)->pd.DataFrame:
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