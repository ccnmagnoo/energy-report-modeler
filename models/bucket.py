from dataclasses import dataclass, fields
from models.components import Component, Specs
from models.econometrics import Cost, Currency

@dataclass
class BucketItem:
    "unit operation charge"
    gloss:str
    description:str
    details:Specs
    quantity:int
    unit:Cost
    cost:Cost

    def __dict__(self)->dict[str:str]:
        tmp={}
        for att in fields(self):
            tmp[att.name]=str(getattr(self,att.name))
        return tmp

class Bucket:
    """contains list of materials and operations required fo project
    >>> methods
        ... subtotal(currency): total amount before overloads
        ... overloads(curr): calc overloads cost
        ... total(curr): net worth after overloads
            ... total().tax() : tax amount
            ... total().gross(): total gross
    """

    items:list[BucketItem]=[]

    def __init__(self,**overloads:float):
        self._overloads=overloads

    def add_item(self,gloss:str,*items:Component):
        """increment and ordered bucket list"""
        for it in items:
            self.items.append(BucketItem(
                gloss=gloss,
                description=it.description,
                details=it.specification,
                quantity=it.quantity,
                unit=it.cost,
                cost=Cost(net_value=it.cost.value*it.quantity,currency=it.cost.currency)
                ))

    def subtotal(self,currency:Currency=Currency.CLP)->Cost:
        """total net value"""
        # res:Cost = sum(list(map(lambda it:it.cost,self.items)))
        cost = Cost(currency=currency)
        for item in self.items:
            cost+=item.cost

        return cost

    def overloads(self,currency=Currency.CLP)->dict[str,Cost]:
        """calcule al overload percentile"""
        ol:dict[str,Cost] = {}
        for load,value in self._overloads.items():
            ol[f'{load} ({value:.0f}%)'] = Cost((value/100)*self.subtotal(currency).net(currency)[0],currency)

        return ol

    def total(self)->Cost:
        """calculate total returning COST handler"""
        wallet:Cost = self.subtotal()
        for _,value in self.overloads().items():
            wallet+=value
        return wallet