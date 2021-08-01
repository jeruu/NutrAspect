import flask
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import pymongo


# assegnazione app
app = Flask(__name__)


# login e inizializzazione db e collection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['NutrAspectProva']
utenti_collection = db['utenti']

# pagina per il login effettuato todo prove
@app.route('/fx', methods=['GET', 'POST'])
def loginRiuscitoProva(query):  # put application's code here

    return '''  <h2>Il login è riuscito!</h2> 
                <h3>name : {}</h3>
                <h3>surname : {}</h3>
                <h3>email : {}</h3>
                '''.format(query['name'], query['surname'], query['email'])


# todo index
@app.route('/', methods=['GET', 'POST'])
def indexProva():
    return render_template('index.html')


# Pagina per il login
@app.route('/login', methods=['GET', 'POST'])
def loginProva():

    # Setup errore
    erroremessaggio = ''

    # Ricaviamo dal post tutti i valori che ci servono per il log in
    email = request.form.get('email')
    password = request.form.get('password')

    # Controlliamo che nessun valore sia nullo, e nel caso procediamo con il controllo di email e password
    if email is not None and password is not None:

        #todo eliminare
        print('POST pieno')
        print(email)
        print(password)

        # Verifica se c'è un utente con la mail inserita
        query = utenti_collection.find_one({"email": email})

        #todo eliminare
        print(query)

        # se la query è andata a buon fine, controlliamo la password, se combaciano si effettua il log in
        if query is not None:
            if query['password'] != password:
                erroremessaggio = 'ErroreLogin'
            else:
                return loginRiuscitoProva(query)

        erroremessaggio = 'ErroreLogin'

    # altrimenti todo
    else:
        print('POST vuoto')

    return render_template('login.html', flash_message=erroremessaggio, messagecaso="DivErrore")


# Pagina per il sign up
@app.route('/register', methods=['GET', 'POST'])
def registerProva():

    # Ricaviamo dal post tutti i valori che ci servono per il sign up
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')

    # Controlliamo che nessun valore sia nullo, e nel caso procediamo con l'inserimento nel database previo controllo
    # di unicità dell'email #TEST
    if email is not None and password is not None and name is not None and surname is not None:
        if not utenti_collection.find_one({"email": email}):
            utenti_collection.insert_one({"email": email, "password": password, "name": name, "surname": surname})
            # TODO pagina registrato successo
            return redirect('/registrato_successo')

    # Altrimenti ritorniamo la pagina del sing up  TODO con errore
    return render_template('register.html')


# Handler per le pagine non trovate
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run()
