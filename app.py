from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import pymongo
import os

app = Flask(__name__)



client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['NutrAspectProva']
utenti_collection = db["utenti"]







@app.route('/fx', methods=['GET', 'POST'])
def loginRiuscitoProva(email):  # put application's code here

    return ''' <h1>{} <- email :D <h1> '''.format(email)


@app.route('/', methods=['GET', 'POST'])
def indexProva():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def loginProva():
    email = request.form.get('email')
    password = request.form.get('password')

    if email is not None and password is not None:
        print('POST pieno')
        print(email)
        print(password)

        print(utenti_collection.find_one({"email": email}))

        if utenti_collection.find_one({"email": email}) is not None:
            return loginRiuscitoProva(email)

    else:
        print('POST vuoto')
    return render_template('login.html')





@app.route('/register', methods=['GET', 'POST'])
def registerProva():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')

    if email is not None and password is not None and name is not None and surname is not None:
        utenti_collection.insert_one({"email": email , "password": password , "email": email , "name": name , "surname": surname})
        return redirect('/')
    return render_template('register.html')


if __name__ == '__main__':
    app.run()
