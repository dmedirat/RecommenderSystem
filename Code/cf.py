# -*- coding: utf-8 -*-
"""CF.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ThvcWFGyRe2e1CSx_rJAlnRcSjT1PJSp
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#links = pd.read_csv('links.csv')
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
#tags = pd.read_csv('tags.csv')

newRatings = ratings.merge(movies, on = 'movieId')

newRatings.head()

ratings['userId'] = ratings['userId'].astype('str')
ratings['movieId'] = ratings['movieId'].astype('str')
movies['movieId'] = movies['movieId'].astype('str')

"""# Statistics of the dataset"""

userId = ratings.userId.unique()
movieId = ratings.movieId.unique()
num_users = len(userId)
num_items =len(movieId)
print('number of unique users:', num_users)
print('number of unique movies:', num_items)

sparsity = 1 - len(ratings) / (num_users * num_items)
print('matrix sparsity:',sparsity)

"""#CF

## Data Sampling
"""

# filtering movies. keeping only those that were rated at least 50 times.
num = 50
# get the number of times a movie has been rated.
movieRatedFreq = pd.DataFrame(ratings.groupby('movieId').size(), columns=['count'])
# get the ID of all movies that have been rated more than 50 times.
popular_movies = list(set(movieRatedFreq.query('count >= @num').index))
# filter the rating DF to contain only the popular movies.
ratingsPopularMovies = ratings[ratings.movieId.isin(popular_movies)]
print('Shape of ratings', ratings.shape)
print('Shape of ratingsPopularMovies', ratingsPopularMovies.shape)

# get the number of times a user has rated a movie.
UserRatedMovieFreq = pd.DataFrame(ratingsPopularMovies.groupby('userId').size(), columns=['count'])
active_users = list(set(UserRatedMovieFreq.query('count >= @num').index))
ratingsPopularMoviesAndUsers = ratingsPopularMovies[ratingsPopularMovies.userId.isin(active_users)]
print('Shape of DF after removing both user and movie < 50:', ratingsPopularMoviesAndUsers.shape)

from scipy.sparse import csr_matrix

# create the sparse matrix
features = ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)
matrix_features = csr_matrix(features.values)
features.head()

temp = movies.copy()
temp.title = temp.title+'|'+temp.movieId

#map movie titles to images
movieToIndex = {
    movie: i for i, movie in 
    enumerate(list(temp.set_index('movieId').loc[features.index].title))
}

"""## KNN"""

from sklearn.neighbors import NearestNeighbors

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
# fit the dataset
model_knn.fit(matrix_features)

matrix_features.shape

"""## Prediction"""

# Build a 1-dimensional array with movie titles
titles = movies['title']
movie_indices = pd.Series(movies.index, index=movies['title'])

def pred(title):
  #this list is the list of recommended movies' ID
  thislist = []
  idx = movie_indices[title]
  distances, indices = model_knn.kneighbors(matrix_features[idx], n_neighbors=20)

  recommended = pd.DataFrame(data=indices[0], columns=['idx'])
  recommended['distances'] = distances[0]
  recommended = recommended.sort_values(by='distances', ascending=False)

  reverse_mapper = {v: k for k, v in movieToIndex.items()}
  for i,row in recommended.iterrows():
    thislist.append(reverse_mapper[row['idx']].split('|')[1])
    print('{0}, with distance of {1}'.format(reverse_mapper[row['idx']], row['distances']))
  return thislist

"""##Calculate ratings from neighbors"""

newRatings = newRatings.drop(labels=['timestamp'],axis=1)

user1 = newRatings.loc[newRatings.userId==257]

user1.movieId = user1.movieId.astype(str)

user1

for i, row in user1.iterrows():
  if(row.movieId in thislist):
    print(row.title)

"""#Case Study

##User 1
"""

recMovieIdUser1 = pred('Dragonheart (1996)')

movies[movies['movieId'].isin(recMovieIdUser1)]

"""##User 2"""

movies[movies['movieId']=='59421'].title

recMovieIdUser2 = pred('What Happens in Vegas... (2008)')

movies[movies['movieId'].isin(recMovieIdUser2)]

"""##User 3"""

movies[movies['movieId']=='3578'].title

recMovieIdUser3 = pred('Gladiator (2000)')

movies[movies['movieId'].isin(recMovieIdUser3)]
