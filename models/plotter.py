from datetime import datetime
import os
import folium
from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame,ExcelWriter
from html2image import Html2Image
from docxtpl import DocxTemplate
from models.bucket import BucketItem
from models.econometrics import Currency
from models.inventory import Project
#cspell: disable

def generate_docs(project):
    """doct generator fun wrapper"""
    #path
    path = get_path(project)

    #generate tables and store CSV
    to_table(project,path)

    #generate plots and store PNG
    plotter(project,path)

    #load templates
    memory_report = DocxTemplate("templates/memory_template.docx")
    bidding_report = DocxTemplate("templates/bidding_template.docx")

    #fill with context
    memory_report.render(project.context(template=memory_report))
    bidding_report.render(project.context(template=bidding_report))

    #fill with graph
    #set into doc
    plot_list = [
        'plot_consumption_forecast',
        'plot_irradiance',
        'plot_temperature',
        'plot_components',
        'plot_components_irr',
        'plot_components_production',
        'plot_production_performance',
        'plot_performance_frequency',
        'plot_flux',
        'map_location'
    ]

    for plot in plot_list:
        memory_report.replace_pic(plot,path+f'{plot}.png')
        print('replaced plot:',plot)
        
    #set scketch connection_diagram
    memory_report.replace_pic('connection_diagram',f'templates/diagram_{project.connection_type}.png')

    #save docs
    memory_report.save(path+"reporte_memoria_calculo.docx")
    bidding_report.save(path+"reporte_pliegos_técnicos.docx")
    print('work',project,'finish at: ',datetime.now())

def get_path(project:Project)->str:
    """get path name, and if not exists create it"""
    path = 'build/'+f'r_{project.building.city.lower()[:3]}_{project.building.name}/'
    create_path_if_not_exist(path)

    return path

def create_path_if_not_exist(path:str):
    """create new dir"""
    if not os.path.exists(path):
        #create
        os.makedirs(path)

def to_table(
    project:Project,
    path:str
    )->None:
    """generate excel results"""
    data_to_file:dict[str,DataFrame] = {
        'clima':project.weather.get_data(),
        'capacidad':project.energy_production(),
        'performance':project.performance(consumptions=['main']),
        'presupuesto':project.bucket.bucket_df()
    }

    #create path

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
    plot_map(project,path)
    map_to_image(path)

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

    def plot_comp_t(bi:BucketItem)->dict[str,float]:
        return {
            "gloss":bi.gloss,
            "description":bi.description,
            "row_total":bi.cost.net(Currency.CLP)[0]
        }

    bkt = project.bucket.bucket(plot_comp_t)
    bkt_list = [*bkt['items'],*bkt['overloads']]
    bkt_df:DataFrame = DataFrame.from_dict(data=bkt_list) #only items and overloads

    plt.figure(figsize=(7,5))
    p = plt.subplot()

    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, bkt_df.index.size))
    p.pie(
        bkt_df['row_total'],
        labels = bkt_df['description'],
        colors=colors,
        autopct='%1.1f%%'
        )
    p.set_xlabel('')
    p.set_ylabel('')
    p.legend().remove()
    plt.savefig(path+'plot_components'+'.png',dpi=250,)

def plot_components_irr(project:Project,path:str):
    """plot each generation component irradiance on surface"""

    modules = project.production_array()
    n_modules=len(modules )
    fig,axs = plt.subplots(n_modules,1,layout='constrained')
    fig.dpi = 300
    fig.set_size_inches(9,7)

    for i,module in enumerate(modules):

        #pivot table
        pivot = module.fillna(0).pivot_table(
            index='month',
            columns='hour',
            values='IRR_incident'
            )
        #meshgrid
        x,y = np.meshgrid(pivot.columns,pivot.index)
        z = pivot.values
        levels = np.linspace(0,1000,21)

        #matplotlib returns an array on subplots(n,m) > 2x2
        if n_modules == 1:
            a = axs
        else:
            a = axs[i]

        cs= a.contourf(x,y,z,levels=levels,cmap='plasma')
        a.set_xlabel(f'24H (módulo {1+i})')
        a.set_ylabel('Mes')

        plt.colorbar(cs)
        fig.suptitle('Irradiación Incidente media horaria [kW/m2]')
        plt.savefig(path+'plot_components_irr'+'.png',dpi=300)

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
    p.plot(x,production_performance['generation'],label='generación',linewidth=2)
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

def plot_map(project:Project, path:str):
    #init
    geo = project.building.geolocation
    map = folium.Map(location=(geo.latitude,geo.longitude),zoom_start=12)

    #marker
    folium.Marker(
        location=[geo.latitude,geo.longitude],
        tooltip=project.building.name,
        popup=project.building.address,
        icon=folium.Icon(color='blue'),
    ).add_to(map)

    #circle marker
    folium.CircleMarker(
        location=[geo.latitude,geo.longitude],
        radius = 25,
        fill=True,
    ).add_to(map)

    map.save(path+'map_location'+'.html')

def map_to_image(html_path:str)->None:
    """screenshot html map file to png"""
    hti = Html2Image(browser='edge',size=(640,480),output_path=html_path)
    hti.screenshot(
        html_file=html_path+'map_location'+'.html',
        save_as='map_location'+'.png')
