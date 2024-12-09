from dataclasses import dataclass, fields
from models.components import Component
from models.econometrics import Cost, Currency

@dataclass
class BucketItem:
    "unit operation charge"
    gloss:str
    description:str
    quantity:int
    cost:Cost

    def __dict__(self)->dict[str:str]:
        tmp={}
        for att in fields(self):
            tmp[att]=str(getattr(self,att))
        return tmp

class Bucket:
    """contains list of materials and operations required fo project"""

    items:list[BucketItem]=[]

    def __init__(self,**overloads:float):
        self.overloads=overloads

    def add_item(self,gloss:str,*items:Component):
        """increment and ordered bucket list"""
        for it in items:
            self.items.append(BucketItem(
                gloss=gloss,
                description=it.description,
                quantity=it.quantity,
                cost=it.cost
                ))

    def subtotal(self)->Cost:
        """total net value"""
        res:Cost = sum(list(map(lambda it:it.cost,self.items)))
        return res

    def get_overloads(self,currency=Currency.CLP)->dict[str,Cost]:
        """calcule al overload percentile"""
        ol:dict[str,Cost] = {}
        for load,value in self.overloads.items():
            ol[f'{load} [{value:.0f}%]'] = Cost((value/100)*self.subtotal().net(currency),currency)

        return ol

    def get_total(self)->Cost:
        """calculate total returning COST handler"""
        wallet:Cost = self.subtotal()
        for _,value in self.get_overloads().items():
            wallet+=value
        return wallet