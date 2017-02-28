from bs4 import BeautifulSoup
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"
r = requests.get(url)
soup = BeautifulSoup(r.content,"lxml")

#for row in soup('table'):
 #   print(row)

html_table = soup('table')[6]

country = []
year = []
total = []
men = []
women = []

# Find all the <tr> tag pairs, skip the first one, then for each.
for row in html_table.find_all('tr')[1:]:
    # Create a variable of all the <td> tag pairs in each <tr> tag pair,
    col = row.find_all('td')
    #print len(col)
    
html_table = soup('table')[6]

country = []
year = []
total = []
men = []
women = []

# Find all the <tr> tag pairs, skip the first one, then for each.
for row in html_table.find_all('tr')[1:]:
    # Create a variable of all the <td> tag pairs in each <tr> tag pair,
    col = row.find_all('td')
    if len(col) == 12:
         # Create a variable of the string inside 1st <td> tag pair,
        column_1 = col[0].string.strip()
        # and append it
        country.append(column_1)
        
        # Create a variable of the string inside 1st <td> tag pair,
        column_2 = col[1].string.strip()
        # and append it
        year.append(column_2)
        
        #col[2], col[3] do not contain any data
        
        # Create a variable of the string inside 1st <td> tag pair,
        column_5 = col[4].string.strip()
        # and append it
        total.append(column_5)
        
        #col[5], col[6] do not contain any data
        
        column_8 = col[7].string.strip()
        # and append it
        men.append(column_8)
        
        #col[8], col[9] do not contain any data
        
        column_11 = col[10].string.strip()
        # and append it
        women.append(column_11)
        
# Create a variable of the value of the columns
columns = {'country': country, 'year': year, 'total': total, 'men': men, 'women': women}

# Create a dataframe from the columns variable
#Table contain information of people's life expetancy in years
edlife_df = pd.DataFrame(columns)

edlife_df['men'] = edlife_df['men'].astype(int)
edlife_df['women'] = edlife_df['women'].astype(int)
edlife_df['total'] = edlife_df['total'].astype(int)
edlife_df['year'] = edlife_df['year'].astype(int)

#for i in range(len(edlife_df)):
#    edlife_df['country'][[i]] = edlife_df['country'][[i]].to_string().split(" ")[-1]
#edlife_df['country'] = edlife_df['country'].astype(str)

#edlife_df['country'] = edlife_df['country'].astype("category")

"""Plotting!!"""

fig, (a,b,c) = plt.subplots(ncols=3,sharey = True)
sns.distplot(edlife_df['men'],ax=a)
sns.distplot(edlife_df['women'],ax=b)
sns.distplot(edlife_df['total'],ax=c)

g = sns.pairplot(edlife_df[['men','women','total']], palette="Set2", diag_kind="hist", size=2.5)

""" Stats """
edlife_df.mean()
edlife_df.median()

"""GDP Comparison"""

import csv
import sqlite3 as lite



with open('world_bank_data/GDP.csv','rU') as inputFile:
    next(inputFile)
    next(inputFile)
    next(inputFile)
    next(inputFile)
    #print next(inputFile)
    header = next(inputFile)
    real_header = (header[0:15]+header[337:-37])
    #print (real_header)
    inputReader = csv.reader(inputFile)
    con = lite.connect('GDP.db')
    cur = con.cursor()
    
    #Creating Table
    cur.execute("DROP TABLE IF EXISTS gdp")
    cur.execute("CREATE TABLE gdp (country_name TEXT, _1999 INT, _2000 INT, _2001 INT, _2002 INT, _2003 INT, _2004 INT, _2005 INT, _2006 INT, _2007 INT, _2008 INT, _2009 INT, _2010 INT)")
    
    for line in inputReader:
       with con:
            cur.execute('INSERT INTO gdp (country_name, _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010) VALUES ("' + line[0] + '","' + '","'.join(line[43:-6]) + '");')
con.close()

# Reading data from database

con = lite.connect('gdp.db')
cur = con.cursor()

gdp_df = pd.read_sql_query("SELECT * FROM gdp",con)
wrong_columns = list(gdp_df.columns)
#print l
correct_columns = []
correct_columns.append(wrong_columns[0][:7])
#l2 = []
for i in range(len(wrong_columns[1:])):
    temp = wrong_columns[i+1]
    correct_columns.append(temp[1:])
#print l2
coldict = dict(zip(wrong_columns,correct_columns))
#print(coldict)
gdp_df = gdp_df.rename(columns = coldict)

#Common Countries

list1 = list(edlife_df['country'].tolist())
list2 = list(gdp_df['country'].tolist())

common = list(set(list1) & set(list2))
 
#Combine Datasets
gdp = []
men = []
women = []
total = []

for i in common:
    df1 = edlife_df[edlife_df['country'] == i ]
    df2 = gdp_df[gdp_df['country'] == i]
    for i in list(df1['year']):
        men.append(df1.men.iloc[0])
        women.append(df1.women.iloc[0])
        total.append(df1.total.iloc[0])
        gdp.append((df2[str(i)].iloc[0]))

df_final = pd.DataFrame({'total': total, 'men':men, 'women': women, 'gdp': gdp})
#Data Wrangling
df_final = df_final[df_final['gdp'] != str('')]
df_final['gdp'] = df_final['gdp'].astype(float).values
df_final['loggdp'] = np.log(df_final['gdp'])

#Visualization of correlation
g = sns.pairplot(df_final[['loggdp','total','men','women']], palette="Set2", diag_kind="hist", size=2.5, kind = 'reg')
print(df_final.corr())