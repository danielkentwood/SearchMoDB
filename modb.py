import os
from os import path
import pickle
import pandas as pd
# NLP
# import nltk
# nltk.download('stopwords')
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# set(stopwords.words('english'))
# cachedStopWords = stopwords.words("english")
# import numpy as np
import plotly.graph_objects as go
from scipy import ndimage




class database:

	def __init__(self, name):
		self.name = name
		self.years = range(1942,2020)
		self.db_dir = os.getcwd() + '/JSON/' + name + '_db'
		self.word_count_dir = os.getcwd() + '/JSON/' + name + '_db_count'
		# self.past_search_dir = os.getcwd() + '/JSON/' + name + '_db_searches'

		self.open_table()
		# self.open_search_cache()
		self.open_word_count_cache()


	# i/o functions
	def open_table(self):
		with open(self.db_dir, 'r+b') as f:
			self.table = pickle.load(f, encoding='latin1')
			self.table['Text'] = self.table['Text'].str.lower()

	# def create_search_cache(self):
	# 	return False
        # hits=list()
        # for y in years:
        #     hits.append(count_string_by_year(y,string))
        
        # data = {'string':[string],'years':[years], 'hits':[hits]}
        # df = pd.DataFrame(data)
        # df.to_pickle(search_dir)  

	# def open_search_cache(self):
	# 	if path.isfile(self.past_search_dir):
	# 		with open(self.past_search_dir, 'r+b') as f:
	# 			self.search_cache = pickle.load(f, encoding='latin1')
	# 			return True
	# 	else:
	# 		return False

	# def update_search_cache(self):
	# 	return False
	    # hits=list()
	    # for y in self.years:
	    #     hits.append(count_string_by_year(y,string))
	    
	    # data = {'string':[string],'years':[years], 'hits':[hits]}
	    # df2 = pd.DataFrame(data)
	    # df = df.append(df2)    
	    # df.to_pickle(search_dir)  

	# def create_word_count_cache(self):
	# 	tokens = self.table['Text'].apply(tokenize)
	# 	tokens = tokens.apply(remove_stop_words)
	# 	t_len = zip(self.table['Year'],tokens.apply(len))
	# 	yc_df = pd.DataFrame(t_len,columns=['Year','Count'])
	# 	word_count = pd.DataFrame(zip(self.years,[sum(yc_df[yc_df['Year']==y].Count) for y in self.years]),columns=['Year','Count'])
	# 	word_count.to_pickle(self.word_count_dir)
	# 	self.word_count = word_count

	def open_word_count_cache(self):
		if path.isfile(self.word_count_dir):
			with open(self.word_count_dir, 'r+b') as f:
				self.word_count = pickle.load(f, encoding='latin1')
				return True
		else:
			self.create_word_count_cache()

	# def update_word_count_cache(self):
	# 	tokens = self.table[self.table['Year']==cur_year]['Text'].apply(tokenize)
	# 	tokens = tokens.apply(remove_stop_words)
	# 	cur_count = sum(tokens.apply(len))
	# 	# if it changed, save it
	# 	if year_count.Count.iloc[-1]!=cur_count:
	# 	    year_count.Count.iloc[-1]=cur_count
	# 	    year_count.to_pickle(count_dir)  

	def string_hits(self, string):
		hits = [sum(self.table[self.table.Year==year].Text.str.count(string)) for year in self.years]
		return hits

	def string_probability(self,string):
		hits = self.string_hits(string)
		counts = list(self.word_count[self.word_count['Year'].isin(self.years)].Count)
		probs = [float(i) / float(j) for i,j in zip(hits, counts)]
		return probs



class figure:

	def __init__(self):
		self.fig = go.Figure()
		self.fig.data = list()
		self.smoothing = 1

	def clear_traces(self):
		self.fig.data = list()

	def add_trace(self,x,y,string):
		if self.smoothing>0:
			ydata = running_mean(y, self.smoothing)
		else:
			ydata = y

		self.fig.add_trace(
			go.Scatter(
				x = pd.Series(x),
				y = ydata, 
				mode = 'lines+markers',
				name = string))

	def set_axes(self, y_text='Probability'):
		self.fig.update_xaxes(
			title_text='Year',
			title_font=dict(size=18),
			showline=True, 
			linewidth=2, 
			linecolor='black',
			range=[1941, 2020])
		self.fig.update_yaxes(
			title_text=y_text, 
			title_font=dict(size=18),
			showline=True, 
			linewidth=2, 
			linecolor='black')

	def show(self):
		self.fig.show()

	def set_smoothing(self,x):
		self.smoothing = x







# # FUNCTIONS
# def tokenize(text):
# 	tokens = nltk.wordpunct_tokenize(text)
# 	words = [w.lower() for w in nltk.Text(tokens) if w.isalpha()]
# 	return words

# def remove_stop_words(tokenized_text):
# 	filt_text = [w for w in tokenized_text if not w in cachedStopWords]
# 	return filt_text

def running_mean(probs, win_size):
    out = ndimage.gaussian_filter1d(probs, win_size)
    return out

# def running_mean2(x, N):
#     out = np.zeros_like(x, dtype=np.float64)
#     dim_len = x.shape[0]
#     for i in range(dim_len):
#         if N%2 == 0:
#             a, b = i - (N-1)//2, i + (N-1)//2 + 2
#         else:
#             a, b = i - (N-1)//2, i + (N-1)//2 + 1

#         #cap indices to min and max indices
#         a = max(0, a)
#         b = min(dim_len, b)
#         out[i] = np.mean(x[a:b])
#     return out
