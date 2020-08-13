import itertools
from collections import OrderedDict
from statistics import mean
import pandas as pd
from user_genres import other_users_genres
import sys
from paths import ratings_path, movies_path

movie_data = pd.read_csv(movies_path)
ratings_data = pd.read_csv(ratings_path, usecols=["movieId", "rating", "userId"])
movie_data_merged = pd.merge(ratings_data, movie_data, on='movieId')
movie_data_merged['mean'] = pd.DataFrame(movie_data_merged.groupby('movieId')['rating'].mean())
movie_data_merged['rating_counts'] = pd.DataFrame(movie_data_merged.groupby('movieId')['rating'].count())
movie_data_merged = movie_data_merged[movie_data_merged['rating_counts']>=50].sort_values('mean', ascending=False)

def existing_user(userID):
    try:
        if int(userID) > 610:
            print("User doesn't exist")
            sys.exit()
        user_data = (movie_data_merged.loc[movie_data_merged['userId'] == userID])
        user_data = user_data.sort_values('rating', ascending=False).drop_duplicates(subset=['movieId', 'title'], keep='first')
        user_data = user_data.join(user_data.genres.str.split('|', expand=True))
        user_data = user_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5', 5:'genre6', 6:'genre7'}).drop(['genres'], 1)
        filtered_genres = list(user_data["genres"])
        filtered_ratings = list(user_data["rating"])
        filtered_movies = list(user_data["title"])
        
        def favourite_genres():
            genre_list = [ "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", 
            "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]  
            rating_dict = {}
            for variable in genre_list:
                rating_dict[variable] = 0
            for x in range(len(filtered_genres)):
                for y in range(len(genre_list)):
                    if genre_list[y] in filtered_genres[x]:
                        rating_dict[genre_list[y]] = rating_dict[genre_list[y]] + float((filtered_ratings[x])/5)
            rating_dict = OrderedDict(sorted(rating_dict.items(), key=lambda t: t[1], reverse=True))
            x = list(itertools.islice(rating_dict.keys(), 0, 5))
            return x

        mask = (movie_data_merged.loc[movie_data_merged['userId'] == userID])
        recommender_data = movie_data_merged.drop(mask.index)
        mask = recommender_data['title'].isin(filtered_movies)
        recommender_data = recommender_data[~mask]
        recommender_data.drop_duplicates(subset=['movieId', 'title'], keep='first', inplace=True)
        recommender_data = recommender_data.join(recommender_data.genres.str.split('|', expand=True))
        recommender_data = recommender_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5'})
        recommender_data = recommender_data.drop(['genres', 'userId', 'rating'], 1)
        recommender_data["index"] = range(1, len(recommender_data)+1)
        recommender_data.set_index("index", inplace=True)

        def genre_similarity():
            column_list = recommender_data.columns.to_list()
            movie_list = list(recommender_data['title'])
            genre_header_list = []
            listno = []
            movie_genre_dict = {}
            for column in column_list:
                if 'genre' in column:
                    genre_header_list.append(column)
            for each in genre_header_list:
                listno.append(list(recommender_data[each]))
            for size in range(len(listno[0])):
                genre_list = []
                for each in listno:
                    genre_list.append(each[size])
                movie_genre_dict[movie_list[size]] = genre_list 
                #Contains a dict of all possible movies for recommendation and their genres in a list. The key is the movie title, value is list of genres.
            recommendations = {}
            for k,v in movie_genre_dict.items():
                count = 0
                for genre in v:
                    if genre in favourite_genres():
                        count = count + 1
                if count >= 2:
                    recommendations[k] = recommender_data[recommender_data['title'] == k]['mean'].values[0]
            recommendations = OrderedDict(sorted(recommendations.items(), key=lambda t: t[1], reverse=True))
            return recommendations

        def user_similarity():
            global movie_data_merged
            number = 0
            dict_movies = {}
            for k,v in other_users_genres(userId = userID).items():
                for el in favourite_genres():
                    if el in v:
                        number = number + 1
                if number >= 2:
                    new_dataframe = movie_data_merged.loc[movie_data_merged['userId'] == k]
                    new_dataframe = new_dataframe.drop(['mean', 'rating_counts'], 1).sort_values('rating', ascending=False)
                    for movies in list(new_dataframe['title']):
                        dict_movies[movies] = new_dataframe[new_dataframe['title'] == movies]['rating'].values[0]
            dict_movies = OrderedDict(sorted(dict_movies.items(), key=lambda t: t[1], reverse=True))
            return dict_movies

        final_list = []
        for k in genre_similarity().keys():
            for vi in user_similarity().keys():
                if k == vi:
                    final_list.append(k)
        return final_list

    except Exception as ex:
        message = f"An exception of type {type(ex).__name__} occurred. \nArguments: {ex.args}"
        replacements = [',', '(', ')']
        for _ in replacements:
            message = message.replace(_, '')
        print(message) 

def new_user(user_genre_list):
    try:
        def genre_similarity_new():
            all_data = movie_data_merged.sort_values('rating', ascending=False).drop_duplicates(subset=['movieId', 'title'], keep='first')
            all_data = all_data.join(all_data.genres.str.split('|', expand=True))
            all_data = all_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5', 5:'genre6', 6:'genre7'}).drop(['genres'], 1)
            column_list = all_data.columns.to_list()
            movie_list = list(all_data['title'])
            genre_header_list = []
            listno = []
            movie_genre_dict = {}
            for column in column_list:
                if 'genre' in column:
                    genre_header_list.append(column)
            for each in genre_header_list:
                listno.append(list(all_data[each]))
            for size in range(len(listno[0])):
                genre_list = []
                for each in listno:
                    genre_list.append(each[size])
                movie_genre_dict[movie_list[size]] = genre_list 
                #Contains a dict of all possible movies for recommendation and their genres in a list. The key is the movie title, value is list of genres.
            recommendations = {}
            for k,v in movie_genre_dict.items():
                count = 0
                for genre in v:
                    if genre in user_genre_list:
                        count = count + 1
                if count >= 2:
                    recommendations[k] = all_data[all_data['title'] == k]['mean'].values[0]
            recommendations = OrderedDict(sorted(recommendations.items(), key=lambda t: t[1], reverse=True))
            return recommendations

        def user_similarity_new():
            global movie_data_merged
            number = 0
            dict_movies = {}
            for k,v in other_users_genres().items():
                for el in user_genre_list:
                    if el in v:
                        number = number + 1
                if number >= 2:
                    new_dataframe = movie_data_merged.loc[movie_data_merged['userId'] == k]
                    new_dataframe = new_dataframe.drop(['mean', 'rating_counts'], 1).sort_values('rating', ascending=False)
                    for movies in list(new_dataframe['title']):
                        dict_movies[movies] = new_dataframe[new_dataframe['title'] == movies]['rating'].values[0]        
            dict_movies = OrderedDict(sorted(dict_movies.items(), key=lambda t: t[1], reverse=True))
            return dict_movies

        final_list = []
        for k in genre_similarity_new().keys():
            for vi in user_similarity_new().keys():
                if k == vi:
                    final_list.append(k)
        return final_list

    except Exception as ex:
        message = f"An exception of type {type(ex).__name__} occurred. \nArguments: {ex.args}"
        replacements = [',', '(', ')']
        for _ in replacements:
            message = message.replace(_, '')
        print(message)    







# print(user_data)
# print(recommender_data)







# with open(r'work\logs\log2.txt', 'w', encoding='utf-8') as l:
#     user_data.to_string(l)
#     l.write("\n\n\n\n\n\n\n")
#     recommender_data.to_string(l)





































































# movies_to_recommend = list(recommender_data["title"])
# bad = []
# for x in filtered_movies:
#     if x in movies_to_recommend:
#         bad.append(x)
#         movies_to_recommend.remove(x)
# recommender_data = recommender_data[recommender_data['title'].isin(movies_to_recommend)]


    # for k,v in rating_dict.items():
    #     print(k,v)

# recommender_data = recommender_data.drop(['userId', 'rating'], 1)

# recommender_data.to_csv(r'log.txt', sep=',', index=False, header=True)

# recommender_data = movie_data_merged.loc[movie_data_merged["userId"] != userID]

# .values.tolist()

# recommender_data['genres'] = recommender_data.genres.apply(lambda x: x.split('|'))

# recommender_data["index"] = range(1, len(recommender_data)+1)
# recommender_data.set_index("index", inplace=True)
# print(len(recommender_data))


# new_dict = dict(zip(list(recommender_data['title']), list(recommender_data['mean'])))

# from sklearn.neighbors import KNeighborsClassifier
# tags_data = pd.read_csv(r"ml-latest-small/tags.csv", usecols=["movieId", "tag"])



# with open('new.txt', 'w', encoding='utf-8') as n:
#     for k,v in new_dict.items():
#         n.write(f"{k} - {v}\n")

# print(new_dict)
# new_movie_filter = []
# for movie in recommender_data['title']:
#     if movie in new_movie_filter:
#         new_movie_filter.append(movie)
#     else:
#         new_movie_filter.append(movie)



# print("\n")
# print(len(filtered_movies))
# print(len(set(filtered_movies)))
# print(len(movies_to_recommend))
# print(len(set(movies_to_recommend)))

# print(recommender_data.title.unique().shape[0])

# print(recommender_data)
# print(len(set(recommender_data['title'])))
# print(len(list(recommender_data['title'])))
# print(len(recommender_data))
# print("\n", recommender_data.columns.tolist())
# print("\n", mean(counts))
# knn = KNeighborsClassifier(n_neighbors=4, algorithm = 'auto', n_jobs=-1)





# genres_to_look = list(recommender_data['genres'])
# mean_rating_to_look = list(recommender_data['mean'])

# dictionary1 = dict(zip(movies_to_recommend, genres_to_look))
# dictionary2 = dict(zip(movies_to_recommend, mean_rating_to_look))


# movies_genres_dictionary = {k:v for k,v in dictionary1.items() if k not in bad}
# movies_rating_dictionary = {k:v for k,v in dictionary2.items() if k not in bad}




# print("\n")
# print(len(bad))
# print(len(dictionary))
# print(len(movies_genres_dictionary))
# print(len(movies_rating_dictionary))




# print(movie_data_merged.head())
# print(movie_data_merged.groupby('title')['rating'].count().sort_values(ascending=False).head())
# userId = input("Please enter userId: ")

# user_data  = user_data[user_data['rating']>=3.0].sort_values('rating', ascending=False)

# user_data_bad  = user_data[user_data['rating']<=2.5]
# print(user_data_bad.head())
# print("\n")
# print(len(list(user_data["rating"])))
# print(len(list(user_data["genres"])))
# print(list(user_data["genres"]))



# ratings_mean_count["index"] = range(1, len(ratings_mean_count)+1)
# ratings_mean_count.set_index("index", inplace=True)
# ratings_mean_count = ratings_mean_count.loc[ratings_mean_count['userId']!=259]
# print(ratings_mean_count.head())

# ratings_mean_count = pd.DataFrame(movie_data_merged.groupby(['title', 'movieId'])['rating'].mean())
# ratings_mean_count['rating_counts'] = pd.DataFrame(movie_data_merged.groupby(['title', 'userId', 'movieId'])['rating'].count())
# ratings_mean_count = ratings_mean_count[ratings_mean_count['rating_counts']>=50].sort_values('rating', ascending=False)
# print(ratings_mean_count.head())


# user_movie_rating = movie_data_merged.pivot_table(index='userId', columns='title', values='rating')
# specific_user = user_movie_rating['100']
# print(specific_user.head())
# forrest_gump_ratings = user_movie_rating['Forrest Gump (1994)']
# print(forrest_gump_ratings.head())

# movies_like_forest_gump = user_movie_rating.corrwith(forrest_gump_ratings)

# corr_forrest_gump = pd.DataFrame(movies_like_forest_gump, columns=['Correlation'])
# corr_forrest_gump.dropna(inplace=True)
# print(corr_forrest_gump.sort_values('Correlation', ascending=False).head(10))

# corr_forrest_gump = corr_forrest_gump.join(ratings_mean_count['rating_counts'])
# print(corr_forrest_gump[corr_forrest_gump ['rating_counts']>50].sort_values('Correlation', ascending=False).head())




# print("\nColumns of movie_data_merged: ", movie_data_merged.columns.tolist())
# print("\nColumns of movie_data: ", movie_data.columns.tolist())
# print("\nColumns of ratings_data: ", ratings_data.columns.tolist())

# import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set_style('dark')

# plt.figure(figsize=(8,6))
# plt.rcParams['patch.force_edgecolor'] = True
# ratings_mean_count['rating_counts'].hist(bins=50)

# plt.figure(figsize=(8,6))
# plt.rcParams['patch.force_edgecolor'] = True
# ratings_mean_count['rating'].hist(bins=50)
# plt.show()
