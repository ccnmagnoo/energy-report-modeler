from dataclasses import dataclass, fields
from pandas import DataFrame
from models.components import Component, Specs
from models.econometrics import Cost, Currency

@dataclass
class BucketItem:
    """unit operation charge"""
    gloss:str
    description:str|None=None
    details:Specs|None=None
    quantity:int|None=None
    unit:Cost|None=None
    cost:Cost|None=None

    def __dict__(self)->dict[str:str]:
        tmp={}
        for att in fields(self):
            tmp[att.name]=str(getattr(self,att.name)) if getattr(self,att.name) is not None else None
        return tmp

    def local_dict(self)->dict[str:str]:
        """return ES-cl object"""
        
        def str_none(it:str|None):
            return str(it) if it is not None else None

        return {
            'glosa':self.gloss,
            'descripción':str_none(self.description),
            'detalles': f'{self.details:fa}' if self.details is not None else '',
            'cantidad':str_none(self.quantity),
            'unitario':f'{self.unit:n.CLP}' if self.unit is not None else None ,
            'global':f'{self.cost:n.CLP}'  if self.cost is not None else None
            }



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

    def bucket_df(self)->DataFrame:
        """return a text type table for docxtpl insert"""
        #build items
        dict_list = list(map(lambda it:it.local_dict(),self.items))

        #add subtotal
        subtotal:BucketItem = BucketItem(
            gloss='sub-total',
            description=None,
            details=None,
            quantity=None,
            unit=None,
            cost=self.subtotal()
            ).local_dict()

        #overloads
        overloads = [BucketItem(gloss=k,cost=v).local_dict() for k,v in self.overloads().items()]

        #tax & global total
        tax = BucketItem('Imp',cost=Cost(self.total().tax()[0])).local_dict()
        total = BucketItem('Total',cost=self.total()).local_dict()

        joint:list[dict] = [*dict_list,subtotal,*overloads,tax,total]
        
        return DataFrame.from_dict(joint).dropna()
        

