import flask
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import flash
import pymongo


app = Flask(__name__)

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['NutrAspectProva']
utenti_collection = db['utenti']

# set as part of the config
SECRET_KEY = 'many random bytes'

# or set directly on the app
app.secret_key = 'many random bytes'

@app.route('/fx', methods=['GET', 'POST'])
def loginRiuscitoProva(query):  # put application's code here

    return '''  <h2>Il login è riuscito!</h2> 
                <h3>name : {}</h3>
                <h3>surname : {}</h3>
                <h3>email : {}</h3>
                '''.format(query['name'],query['surname'],query['email'])




@app.route('/', methods=['GET', 'POST'])
def indexProva():

    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def loginProva():
    erroremessaggio= ''
    email = request.form.get('email')
    password = request.form.get('password')

    if email is not None and password is not None:

        print('POST pieno')
        print(email)
        print(password)

        query = utenti_collection.find_one({"email": email})
        print(query)

        if utenti_collection.find_one({"email": email}) is not None:

            return loginRiuscitoProva(query)
        erroremessaggio='ErroreLogin'


    else:
        print('POST vuoto')


    return render_template('login.html',flash_message=erroremessaggio, messagecaso="DivErrore")


@app.route('/register', methods=['GET', 'POST'])
def registerProva():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')

    if email is not None and password is not None and name is not None and surname is not None:
        utenti_collection.insert_one(
            {"email": email, "password": password, "name": name, "surname": surname})
        return redirect('/')
    return render_template('register.html')


if __name__ == '__main__':
    app.run()
