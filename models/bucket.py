from dataclasses import dataclass, fields
from typing import Callable, Self
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
    unitary:Cost|None=None
    cost:Cost|None=None

    def __dict__(self)->dict[str:str]:
        tmp={}
        for att in fields(self):
            tmp[att.name]=str(getattr(self,att.name)) if getattr(self,att.name) is not None else None
        return tmp

    def local_dict(self,item:Self|None = None)->dict[str:str]:
        """return ES-cl object"""
        ctx:Self = item if item else self

        def str_none(it:str|None):
            return str(it) if it is not None else None

        return {
            'glosa':ctx.gloss,
            'descripción':str_none(ctx.description),
            'detalles': f'{ctx.details:fa}' if ctx.details is not None else '',
            'cantidad':str_none(self.quantity),
            'unitario':f'{ctx.unitary:n.CLP}' if ctx.unitary is not None else None ,
            'global':f'{ctx.cost:n.CLP}'  if ctx.cost is not None else None
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
                unitary=it.cost,
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

    def set_overloads(self,**overloads:float):
        """add or patch overloads values"""
        self._overloads.update(overloads)

    def reset_overloads(self):
        """reset overloads to ZERO"""
        self._overloads = {}

    def total(self)->Cost:
        """calculate total returning COST handler
        >>> Format (eg: net.CURRENCY):
         net = net value
         gross= gross value
         CURRENCY = USD, UF, CLP, EUR available
        """
        wallet:Cost = self.subtotal()
        for _,value in self.overloads().items():
            wallet+=value
        return wallet

    def bucket(self,fn:Callable[[BucketItem],dict]=BucketItem.local_dict)->dict[str,list[dict]]:
        """return a text type table for docxtpl insert"""
        #build items


        #add subtotal
        subtotal:BucketItem = BucketItem(
            gloss='sub-total',
            description='equipamiento neto',
            details=None,
            quantity=None,
            unitary=None,
            cost=self.subtotal()
            )

        #overloads
        overloads = [BucketItem(gloss=k,description=k,cost=v) for k,v in self.overloads().items()]

        #tax & global total
        total = BucketItem('Total',description='total neto s/iva',cost=self.total())
        tax = BucketItem('Imp (19%)',description='valor IVA',cost=Cost(self.total().tax()[0]))

        joint:dict[str,list[BucketItem]] = {
            "items":self.items,
            "subtotal":[subtotal],
            "overloads":overloads,
            "total":[total],
            "tax":[tax],
            }

        #local
        joint_mod = {group_name:list(map(fn,pack)) for group_name,pack in joint.items()}
        return joint_mod

    def _flat_bucket(self,fn:Callable[[BucketItem],dict]=BucketItem.local_dict)->list[dict]:
        lst =  [v for _,v in self.bucket(fn).items()]
        ctx:list[dict] = []
        for it in lst:
            for i in it:
                ctx.append(i)

        return ctx


    def bucket_df(self,fn:Callable[[BucketItem],dict]=BucketItem.local_dict)->DataFrame:
        """return dict as a DataFrame with covered None
        >>> df params
        - "glosa","descripción","detalles","cantidad","unitario","global"
        """
        return DataFrame.from_dict(self._flat_bucket(fn)).fillna('')
    
    def gx_bucket_df(self,generate_tag='generación',)->DataFrame:
        """
        >>> df params        - "glosa","descripción","detalles","cantidad","unitario","global"
        """
        df = self.bucket_df()
        return df[df['glosa']==generate_tag]