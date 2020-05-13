import os
import pickle

import pandas as pd
import plotly.graph_objects as go
from scipy import ndimage



class Database:
    """
    Instantiates a database object by loading JSON files.
    """

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

	def open_word_count_cache(self):
		if path.isfile(self.word_count_dir):
			with open(self.word_count_dir, 'r+b') as f:
				self.word_count = pickle.load(f, encoding='latin1')
				return True
		else:
			self.create_word_count_cache()

	def string_hits(self, string):
		hits = [sum(self.table[self.table.Year==year].Text.str.count(string)) for year in self.years]
		return hits

	def string_probability(self,string):
		hits = self.string_hits(string)
		counts = list(self.word_count[self.word_count['Year'].isin(self.years)].Count)
		probs = [float(i) / float(j) for i,j in zip(hits, counts)]
		return probs



class Figure:
    """
	Helper class to plot a histogram of search term hits over time.
    """

	def __init__(self):
		self.fig = go.Figure()
		self.fig.data = list()
		self.smoothing = 1

	def clear_traces(self):
		self.fig.data = list()

	def add_trace(self, x, y, curve_label):
        """
        Plot the curve using x y data.

        Arguments
        ---------

        x: The x axis data (datetime series).
        y: The search term frequencies.
        curve_label: The label to be associated with the curve on the plot.
        """

		# Smoothen curve by applying a rolling mean if smoothing is defined
		ydata = running_mean(y, self.smoothing) if self.smoothing else y

        # Plot the curve
		self.fig.add_trace(
			go.Scatter(
				x=pd.Series(x),
				y=ydata,
				mode='lines+markers',
				name=curve_label
            )
        )

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

	def set_smoothing(self, x):
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
