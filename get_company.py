import re

# 3. select and plot USA/CHN companies usage of CI from old dataset
# use regEx to get company name from markdown file
f = open("jiayun-README.md")
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

print(USA_COMP)
print(China_COMP)