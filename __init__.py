import os
from flask import (Flask, flash, redirect, render_template, request, session, url_for)
from helper import existing_user, new_user
import json

app = Flask(__name__)
app.secret_key = str(os.urandom(24))

@app.route('/', methods=['POST', 'GET'])
def work():
    genre_list = [ "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", 
    "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"] 
    length = len(genre_list)
    if request.method == 'POST':
        try:
            userId = request.form.get('fname1')
            return render_template('results.html', recommendations = existing_user(int(userId)), identifier = 'existing user') 
        except:
            var = []
            for el in range(length):
                if request.form.get(f'genre_name{el}') != None:
                    var.append(request.form.get(f'genre_name{el}'))
            return render_template('results.html', recommendations = new_user(var), identifier = 'new user')  
    return render_template('draft.html', genre_list=genre_list, length=length)

if __name__ == "__main__":
    # app.run(debug=True, port=8080)
    app.run()





# To debug using VScode, remove the debug=True option




# print(existing_user(45))
# print(new_user(['Action', 'Adventure', 'Crime', 'Documentary', 'Film-Noir', 'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War']))



# print(userId)
# print(var)
# # recommendations = json.dumps(new_user(var))
# recommendations = new_user(var)
# identifier = 'new user'


# print(userId)
# # recommendations = json.dumps(existing_user(userId))
# recommendations = existing_user(userId)
# identifier = 'existing user'