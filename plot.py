import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker
from scipy import stats
import numpy as np

df = pd.read_csv("CloneTest6_2022-09-26.csv",usecols=['language','GHA','Travis'])
df["GHA"]=df["GHA"].map({True:1,False:0})
df["Travis"]=df["Travis"].map({True:1,False:0})

# remove languages used by less than 20 repos
df2=df.groupby('language').filter(lambda x:x['language'].value_counts()>20)
print(df2)

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

df2['Both'] = df2.apply(lambda x: both(x.GHA, x.Travis), axis = 1) 
df2['Neither'] = df2.apply(lambda x: neither(x.GHA, x.Travis), axis = 1) 
group_sum = df2.groupby('language').agg('sum')
group_avg = df2.groupby('language').agg('mean')



# draw language graph with num
# group_sum.plot(kind='bar',xlabel='language',ylabel='num_of_repos',logy=True)



# draw language graph with precentage
# group_avg.plot(kind='bar',xlabel='language',ylabel='percentage')
# def to_percent(temp, position):
#     return '%1.0f'%(100*temp) + '%'
# plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))



# function for plotting last 5 graphs
def num_plot(col):
    df_GHA = pd.read_csv("CloneTest6_2022-09-26.csv",usecols=[col,'GHA'])
    df_TRA = pd.read_csv("CloneTest6_2022-09-26.csv",usecols=[col,'Travis'])
    
    # compute the p value of two samples, using stats.ttest_ind to do the T test
    # applied_GHA = df_GHA[df_GHA['GHA']==True]
    # applied_TRA = df_TRA[df_TRA['Travis']==True]
    # test = stats.ttest_ind(list(applied_GHA['pr_num']),list(applied_TRA['pr_num']),equal_var=False)
    # print(test)
    
    GHA_group = df_GHA.groupby('GHA').agg('mean')
    print(df_GHA)
    TRA_group = df_TRA.groupby('Travis').agg('mean')
    GHA_group = GHA_group.rename(columns={col:'GHA'}).T.rename(columns={True:'Applied',False:'Not Applied'})
    TRA_group = TRA_group.rename(columns={col:'Travis'}).T.rename(columns={True:'Applied',False:'Not Applied'})
    single_merge = pd.concat([GHA_group,TRA_group])


    df = pd.read_csv("CloneTest6_2022-09-26.csv",usecols=[col,'GHA','Travis'])
    both = df[(df['GHA']) & (df['Travis'])]
    neither = df[~(df['GHA']) & ~(df['Travis'])]
    both_group = both.groupby(['GHA','Travis']).agg('mean')
    not_group = neither.groupby(['GHA','Travis']).agg('mean')
    both_merge = pd.concat([not_group,both_group])
    both_merge = both_merge.reset_index(drop=True).rename(columns={col:"Using both/neither"}).T.rename(columns={1:'Applied',0:'Not Applied'})
    all = pd.concat([single_merge,both_merge])
    return all.plot(kind='bar',xlabel='Using of CIs',ylabel=col+' per repo')



# draw issue_comments_num graph
# num_plot('issue_comments_num')

# draw commit_comments_num graph
# num_plot('commit_comments_num')

# draw pr_comments_num graph
# num_plot('pr_comments_num')

# draw pr_num graph
num_plot('pr_num')

# draw forks_count graph
# num_plot('forks_count')

plt.xticks(rotation=45)
# plt.show()