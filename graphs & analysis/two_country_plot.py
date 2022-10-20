import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker
from scipy import stats
import numpy as np
import re

def both(a,b):
    if(a+b == 2):
        return 1
    else:
        return 0

def neither(a,b):
    if(a+b==0):
        return 1
    else:
        return 0

def to_percent(temp, position):
    return '%1.0f'%(100*temp) + '%'


# 1. plot the average percentage usage of CIs of two countries from newly crawled dataset

# together = pd.read_csv("USA&PRC.csv",usecols=['Country','GHA','Travis'])

# together['Both'] = together.apply(lambda x: both(x.GHA, x.Travis), axis = 1) 
# # together['Neither'] = together.apply(lambda x: neither(x.GHA, x.Travis), axis = 1) 

# group_avg = together.groupby('Country').agg('mean').T
# group_avg.plot(kind='bar',xlabel='CI (from newly crawled dataset)',ylabel='usage percentage')
# plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))




# 2. plot the average percentage usage of CIs of two countries' companies from newly crawled dataset

# df = pd.read_csv("USA&PRC.csv",usecols=['ORG','Country','GHA','Travis'])
# df["GHA"]=df["GHA"].map({True:1,False:0})
# df["Travis"]=df["Travis"].map({True:1,False:0})

# df['Both'] = df.apply(lambda x: both(x.GHA, x.Travis), axis = 1) 
# # df['Neither'] = df.apply(lambda x: neither(x.GHA, x.Travis), axis = 1)

# df_usa = df[df['Country']=='USA'].drop('Country',axis=1)
# df_chn = df[df['Country']=='CHN'].drop('Country',axis=1)

# usa_avg = df_usa.groupby('ORG').agg('mean')
# chn_avg = df_chn.groupby('ORG').agg('mean')

# fig,axes = plt.subplots(1,2)  

# ax1 = axes[0]  
# usa_avg.plot(kind='bar',xlabel='American Companies (from newly crawled dataset)',ylabel='repo usage percentage',ax=ax1)
# ax1.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))

# ax2 = axes[1]
# chn_avg.plot(kind='bar',xlabel='Chinese Companies (from newly crawled dataset)',ax=ax2)
# ax2.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))





# 3. select and plot USA/CHN companies usage of CI from old dataset
# use regEx to get company name from markdown file
f = open("/Users/andyluo/Desktop/README.md")
md = f.read()
f.close()
temp = re.findall(r'####.*',md)

# clean the company name
comp = []
for c in temp:
    comp.append(c.replace("#### ",""))

USA_COMP = comp[:comp.index('alibaba')]
China_COMP = comp[comp.index('alibaba'):]

# 'uber' 'Instagram' 'airbnb' 'citrix' are classified to China companies in markdown by mistaken, need to fix
bugs = ['uber','Instagram','airbnb','citrix']
for b in bugs:
    USA_COMP.append(b)
    China_COMP.remove(b)

# get the according repos from old csv dataset 
raw_dt = pd.read_csv("CloneTest6_2022-09-26.csv",usecols=['organization_name','GHA','Travis'])

# get the target companies repo
def in_comp(x):
    global comp
    x = str(x)
    for c in comp:
        if(c.lower() in x.lower()):
            return True
    return False

def country(x):
    global USA_COMP
    x = str(x)
    for c in USA_COMP:
        if(c.lower() in x.lower()):
            return 'USA'
    return 'CHN'

raw_dt['Valid'] = raw_dt.apply(lambda x: in_comp(x.organization_name), axis = 1) 
comp_dt = raw_dt[raw_dt['Valid']==True].drop('Valid',axis=1)
comp_dt['Country'] = comp_dt.apply(lambda x: country(x.organization_name), axis = 1)
comp_dt['Both'] = comp_dt.apply(lambda x: both(x.GHA, x.Travis), axis = 1) 
# comp_dt['Neither'] = comp_dt.apply(lambda x: neither(x.GHA, x.Travis), axis = 1) 


# plot two countries graph

# country_group = comp_dt.groupby('Country').agg('mean').T
# country_group.plot(kind='bar',xlabel='CI (from old dataset)',ylabel='usage percentage')
# plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))


# plot companies graph

usa_dt = comp_dt[comp_dt['Country']=='USA'].drop('Country',axis=1)
chn_dt = comp_dt[comp_dt['Country']=='CHN'].drop('Country',axis=1)

def rename(x,country):
    global USA_COMP,China_COMP
    if(country == 'USA'):
        for c in USA_COMP:
            if(c.lower() in x.lower()):
                return c
    else:
        for c in China_COMP:
            if(c.lower() in x.lower()):
                return c

usa_dt['ORG'] = usa_dt.apply(lambda x: rename(x.organization_name, 'USA'), axis = 1)
chn_dt['ORG'] = chn_dt.apply(lambda x: rename(x.organization_name, 'CHN'), axis = 1)

usa_dt = usa_dt.drop('organization_name',axis=1)
chn_dt = chn_dt.drop('organization_name',axis=1)

usa_dt_avg = usa_dt.groupby('ORG').agg('mean')
chn_dt_avg = chn_dt.groupby('ORG').agg('mean')

fig2,axes2 = plt.subplots(1,2)  

ax3 = axes2[0]  
usa_dt_avg.plot(kind='bar',xlabel='American Companies (from old dataset)',ylabel='repo usage percentage',ax=ax3)
ax3.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))

ax4 = axes2[1]
chn_dt_avg.plot(kind='bar',xlabel='Chinese Companies (from old dataset)',ax=ax4)
ax4.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))

plt.show()