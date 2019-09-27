import pandas as pd
import pickle
import os
from os import path
import datetime

# NLP
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
set(stopwords.words('english'))
cachedStopWords = stopwords.words("english")



# write a function to tokenize text and remove stop words
def tokenize_no_stop(text):
    tokens = nltk.wordpunct_tokenize(text)
    words = [w.lower() for w in nltk.Text(tokens) if w.isalpha()]
    # remove stop words
    filt_text = [w for w in words if not w in cachedStopWords]
    return filt_text

# write a function to tokenize text (and keep stop words)
def tokenize_with_stop(text):
    tokens = nltk.wordpunct_tokenize(text)
    words = [w.lower() for w in nltk.Text(tokens) if w.isalpha()]
    return words  

# write a function to open the desired table and update the word count cache file
def open_table(table_name):
    cache_dir = os.getcwd() + '/JSON/' + table_name + '_db'
    count_dir = os.getcwd() + '/JSON/' + table_name + '_db_count'

    f = open(cache_dir, 'r+b') # 'r+b' means that you're opening it as readable, writable, and binary
    db = pickle.load(f)
    # Make the text column lowercase
    db['Text'] = db['Text'].str.lower()
    
    cur_month_str = datetime.datetime.today().strftime('%Y/%m')
    cur_year = int(cur_month_str[0:4])

    if path.isfile(count_dir):
        # if it count cache file already exists, load it
        f = open(count_dir, 'r+b') # 'r+b' means that you're opening it as readable, writable, and binary
        year_count = pickle.load(f)
        # update current year
        tokens = db[db['Year']==cur_year]['Text'].apply(tokenize_with_stop)
        cur_count = sum(tokens.apply(len))
        # if it changed, save it
        if year_count.Count.iloc[-1]!=cur_count:
            year_count.Count.iloc[-1]=cur_count
            year_count.to_pickle(count_dir)
        
    else:
        # otherwise, create count cache file and save it
        tokens = db['Text'].apply(tokenize_with_stop)
        t_len = zip(db['Year'],tokens.apply(len))
        yc_df = pd.DataFrame(t_len,columns=['Year','Count'])
        years=range(1942,cur_year+1)
        year_count = pd.DataFrame(zip(years,[sum(yc_df[yc_df['Year']==y].Count) for y in years]),columns=['Year','Count'])
        year_count.to_pickle(count_dir)
        
    return db



# count the number of times a string appears in a body of text
def count_string_hits(text, string):
    t = pd.Series(text)
    s_sum = sum(t.str.count(string))
    return s_sum


# count the number of times a string appears in a given year
def count_string_by_year(year, string, db):
    csy=0
    for x,y in enumerate(db[db.Year==year]['Text']):    
        if len(y)!=0:
            ss = count_string_hits(y,string)
            csy+=ss
    return csy


def get_probs_for_years(years,string):
    count_dir = os.getcwd() + '/JSON/GC_db_count'
    f = open(count_dir, 'r+b') # 'r+b' means that you're opening it as readable, writable, and binary
    year_count = pickle.load(f)
    counts = list(year_count[year_count['Year'].isin(years)].Count)
    
    # see if we have a search cache yet
    search_dir = os.getcwd() + '/JSON/GC_db_searches'
    if path.isfile(search_dir):
        # if yes, then open it
        f = open(search_dir, 'r+b') # 'r+b' means that you're opening it as readable, writable, and binary
        df = pickle.load(f)
        # see if your search term is there
        searched = df[df.string==string]
        # if it's there, grab the hits
        if len(searched)>0:
            hits=searched.hits[0]
        # if not, compute the hits and add to the search cache    
        else:
            hits=list()
            db = open_table('GC')
            for y in years:
                hits.append(count_string_by_year(y,string,db))
            
            data = {'string':[string],'years':[years], 'hits':[hits]}
            df2 = pd.DataFrame(data)
            df = df.append(df2)    
            df.to_pickle(search_dir)           
    else:
        # if the search cache doesn't exist, compute the hits for the first search term and save it to the cache
        hits=list()
        table_name = 'GC'
        db = open_table(table_name)
        for y in years:
            hits.append(count_string_by_year(y,string,db))
        
        data = {'string':[string],'years':[years], 'hits':[hits]}
        df = pd.DataFrame(data)
        df.to_pickle(search_dir)  

    probs = [float(i) / float(j) for i, j in zip(hits, counts)] 
    return probs

