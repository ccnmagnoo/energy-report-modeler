from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame,ExcelWriter
from models.econometrics import Currency
from models.inventory import Project
#cspell: disable

def toTable(project:Project,path:str)->None:
    """generate excel results"""
    data_to_file:dict[str,DataFrame] = {
        'clima':project.weather.get_data(),
        'capacidad':project.energy_production(),
        'performance':project.performance(consumptions=['main']),
    }

    for key,data in data_to_file.items():
        with ExcelWriter(path+f'calc_{project.building.city}_{project.building.name}_{key}.xlsx') as writer:#pylint: disable=abstract-class-instantiated
            data.to_excel(writer,sheet_name='result')

def plotter(project:Project,path:str)->None:
    """plot all"""
    #aux
    f=project.building.consumptions['main'].forecast()
    w = project.weather.get_data()
    #plotting
    plot_consumption_forecast(f,path)
    plot_irradiance(w,path)
    plot_temperature(w,path)
    plot_components(project,path)
    plot_components_irr(project,path)
    plot_components_production(project,path)
    plot_production_performance(project,path)
    plot_performance_frecuency(project,path)
    plot_flux(project,path)

    print('plot_done')


def plot_consumption_forecast(forecast:DataFrame,path:str):
    """consumption forecast line plot"""
    p = plt.subplot()
    p.plot(forecast['month'],forecast['energy'],linewidth=3)
    p.set_xlabel('mes')
    p.set_ylabel('consumo [kWH]')
    plt.savefig(path+'plot_consumption_forecast'+'.png',dpi=300)

def plot_irradiance(weather:DataFrame,path:str):
    """irradiance plot saving"""
    plt.figure(figsize=(10,4))
    p = plt.subplot()
    w = weather
    g= w[['month','day','ALLSKY_SFC_SW_DNI','ALLSKY_SFC_SW_DIFF']]\
        .groupby(['month','day'],as_index=False).mean()
    p.plot(
        g.index.values,
        g['ALLSKY_SFC_SW_DNI'].values,
        label='directa',
        linewidth=.75
        )
    p.plot(
        g.index.values,
        g['ALLSKY_SFC_SW_DIFF'].values,
        label='difusa',
        linewidth=.75
        )
    p.set_xlabel('dia N')
    p.set_ylabel('irradiación media por día W/m2')
    plt.legend()
    plt.savefig(path+'plot_irradiance'+'.png',dpi=350)

def plot_temperature(weather:DataFrame,path:str):
    """temperature max,min, avg  line plot"""
    plt.figure(figsize=(10,4))
    p = plt.subplot()
    w = weather
    g_max= w[['month','day','T2M',]].groupby(['month','day'],as_index=False).max()
    g_min= w[['month','day','T2M',]].groupby(['month','day'],as_index=False).min()
    g_men= w[['month','day','T2M',]].groupby(['month','day'],as_index=False).mean()
    p.plot(
        g_men.index,
        g_men['T2M'],
        label='T° media [°C]',
        linewidth=.75,
        )
    p.fill_between(
        g_men.index,
        g_max['T2M'],
        g_min['T2M'],
        alpha=.5,
        color='orange',
        label='T [°C] max/min'
        )

    p.set_xlabel('dia N')
    p.set_ylabel('Temp Promedio [°C]')
    plt.legend()
    plt.savefig(path+'plot_temperature'+'.png',dpi=350)

def plot_components(project:Project,path:str):
    """plot components cost pie plot"""
    bucket = project.bucket_list(currency=Currency.CLP)['bucket']
    plt.figure(figsize=(5,5))
    p = plt.subplot()

    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, bucket.index.size))
    p.pie(
        bucket['cost_after_tax'],
        labels = bucket['description'],
        colors=colors,
        autopct='%1.1f%%'
        )
    p.set_xlabel('')
    p.set_ylabel('')
    p.legend().remove()
    plt.savefig(path+'plot_components'+'.png',dpi=300)

def plot_components_irr(project:Project,path:str):
    """plot each generation component irradiance on surface"""

    modules = project.production_array()

    fig,axs = plt.subplots(len(modules),1,layout='constrained')
    fig.dpi = 300
    fig.set_size_inches(9,7)

    for i,module in enumerate(modules):

        #pivot table
        pivot = module.fillna(0).pivot_table(index='month',columns='hour',values='IRR_incident')
        #meshgrid
        x,y = np.meshgrid(pivot.columns,pivot.index)
        z = pivot.values
        levels = np.linspace(0,1000,20)
        cs= axs[i].contourf(x,y,z,levels=levels,cmap='plasma')
        plt.colorbar(cs)

        axs[i].set_xlabel(f'24H (módulo {1+i})')
        axs[i].set_ylabel('Mes')

        fig.suptitle('Irradiación Incidente media horaria [kW/m2]')
        plt.savefig(path+'plot_components_irr'+'.png',dpi=305)

def plot_components_production(project:Project,path:str):
    """plot energy generation on 12 month, line plot"""
    #plot_components_production
    #source
    modules = project.production_array()
    #plotter
    plt.figure(figsize=(10,6))
    axs = plt.subplot()

    for i,module in enumerate(modules):
        #pivot table
        group = module[['month','day','System_capacity_KW']].groupby(['month'],as_index=False).sum()
        #meshgrid
        axs.plot(group.index,group['System_capacity_KW'],label=f'modulo {i+1}')
        axs.set_xlabel('mes N')
        axs.set_ylabel('Generación kWh/mes')

        for i, value in enumerate(group['System_capacity_KW'].round(0).values):
            plt.text(group.index[i], group['System_capacity_KW'][i], value, ha='center', va='bottom')
    plt.legend()
    plt.savefig(path+'plot_components_production'+'.png',dpi=300)

def plot_production_performance(project:Project,path:str):
    """bar plot of generation, netbilling, total savings"""
    #plot_production_performance
    performance = project.performance(consumptions=['main'])
    production_performance = performance[['month','consumption','generation','netbilling','savings']]

    plt.figure(figsize=(10,5),dpi=300)
    p = plt.subplot()
    x = production_performance['month']
    p.plot(x,production_performance['consumption'],'o--',label='demanda')
    p.plot(x,production_performance['generation'],label='generación',linewidth=4)
    sv=p.bar(x,production_performance['savings'],label='ahorro',width=0.5)
    nb= p.bar(x,production_performance['netbilling'],label='netbilling',width=0.4)
    p.bar_label(sv,label_type='center',fmt='%.0f',color='w')
    p.bar_label(nb,label_type='edge',fmt='%.0f', color='orange')

    p.set_xlabel('mes')
    p.set_ylabel('energía [kWH]')

    plt.legend()
    plt.savefig(path+'plot_production_performance'+'.png',dpi=300)

def plot_performance_frecuency(project:Project,path:str):
    """2D diagram for operation frecuencry across a day"""
    #plot_performance_frequency

    plt.figure(dpi=300,layout='constrained')
    fig,p = plt.subplots()
    fig.set_size_inches(8,5)
    fig.set_dpi(300)
    x = project.energy_production()['hour']
    y = project.energy_production()['System_capacity_KW']
    hb = p.hexbin(x,y,gridsize=12,cmap='plasma')
    plt.colorbar(hb)

    p.set_xlabel('Horario')
    p.set_ylabel('Potencia [kW]')
    fig.legend()
    plt.savefig(path+'plot_performance_frequency'+'.png',dpi=300)

def plot_flux(project:Project,path:str):
    """finnacial analysis profit generatio"""
    #plot_flux
    fin = project.economical_analysis(currency=Currency.CLP)

    plt.figure(figsize=(10,4),dpi=300)
    data = DataFrame({"flujo":fin['flux'],"acumulado":fin['accumulated']})
    p = plt.subplot()
    bar=p.bar(data.index,data['flujo']/1000,width=.8,label='flujo')
    line=p.plot(data.index,data['acumulado']/1000,color='orange',marker='o',linewidth=3,label='flujo acumulado')

    #label
    p.bar_label(bar,label_type='center',fmt='%.0f',color='w')
    p.set_xlabel('año')
    p.set_ylabel('utilidades Miles$CLP')

    for i, value in enumerate(data['acumulado'].round(0).values):
        plt.text(data.index[i], (data['acumulado']/1000)[i], f'{value/1000:.0f}', ha='center', va='bottom',color='#045993',)
    plt.legend()
    plt.savefig(path+'plot_flux'+'.png',dpi=300)