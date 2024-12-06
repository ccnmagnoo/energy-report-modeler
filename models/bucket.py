from dataclasses import dataclass, fields
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
    items:list[BucketItem]
    def __init__(self,tax:float, **overloads:float):
        self.tax=tax,
        self.overloads=overloads

    def add_item(self,*items:BucketItem):
        """increment and ordered bucket list"""
        for it in items:
            self.items.append(it)

    def net(self,round=2,currency=Currency.CLP)->float:
        """total net value"""
        return round(sum(list(map(lambda it:it.cost.cost_before_tax(currency),self.items))),round)

    def gross(self,round=2,currency=Currency.CLP)->float:
        """total gross value BEFORE overloads"""
        return round(sum(list(map(lambda it:it.cost.cost_before_tax(currency),self.items))),round)
    
    def get_overloads(self,currency=Currency.CLP)->dict[str,float]:
        """calcule al overload percentile"""
        ol:dict[str,float] = {}
        for load,value in self.overloads.items():
            ol[f'{load} [{value:.0f}%]'] = Cost((value/100)*self.net(),currency).cost_before_tax(currency)
        return ol
    def get_total(self)->Cost:
        wallet:float = self.net()
        for _,value in self.get_overloads().items():
            wallet+=value
        total = Cost(wallet)