import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from fitness import *

import flask_login
import pymongo

# assegnazione app e chiave segreta
app = Flask(__name__)
app.secret_key = 'chiavesecreta'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# login e inizializzazione db e collection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['NutrAspect']
users_collection = db['users']
dailyWeight_collection = db['dailyWeight']
dailyWater_collection = db['dailyWater']
foodList_collection = db['foodList']
dailyFood_collection = db['dailyFood']

# avvio del server flask
if __name__ == '__main__':
    app.run()


# Creazione classe user
class User(flask_login.UserMixin):
    pass


# Loader dell'utente, dove viene assegnato per comodità l'email come id
@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user


# Pagina root e principale del sito
@app.route('/', methods=['GET', 'POST'])
def indexPage():
    return render_template('index.html')


# Homepage dell'area utente
@app.route('/home', methods=['GET', 'POST'])
@flask_login.login_required
def homePage():
    # inizializzazione di valori e coefficienti
    # recupero degli alimenti consumati in data odierna
    uEmail = flask_login.current_user.id

    foodDate = todayDate()
    if 'foodDate' in request.args:
        foodDate = request.args['foodDate']
        foodDate = datetime.datetime.strptime(foodDate, '%Y-%m-%d')

    dailyMeal = dailyFood_collection.find_one({'userEmail': uEmail, 'day': foodDate})
    dailySummary = []

    calTemp = 0
    carbTemp = 0
    protTemp = 0
    fatTemp = 0

    carbCoeff = .4 / 4
    protCoeff = .3 / 4
    fatCoeff = .3 / 9

    # dump dei dati dal record in mongodb ai vettori divisi per pasto
    foodArrBreakfast = foodArrDump(dailyMeal, 'Breakfast')
    foodArrLaunch = foodArrDump(dailyMeal, 'Launch')
    foodArrDinner = foodArrDump(dailyMeal, 'Dinner')
    foodArrSnack = foodArrDump(dailyMeal, 'Snack')

    # somma totale di tutti i nutrimenti della giornata
    for food in foodArrBreakfast:
        calTemp += food[2]
        carbTemp += food[3]
        protTemp += food[4]
        fatTemp += food[5]

    for food in foodArrLaunch:
        calTemp += food[2]
        carbTemp += food[3]
        protTemp += food[4]
        fatTemp += food[5]

    for food in foodArrDinner:
        calTemp += food[2]
        carbTemp += food[3]
        protTemp += food[4]
        fatTemp += food[5]

    for food in foodArrSnack:
        calTemp += food[2]
        carbTemp += food[3]
        protTemp += food[4]
        fatTemp += food[5]

    # Recupero delle calorie giornaliere e calcolo dei nutrimenti totali consigliati
    calD = int(users_collection.find_one({'email': uEmail})['dCal'])
    carbTot = int(calD * carbCoeff)
    protTot = int(calD * protCoeff)
    fatTot = int(calD * fatCoeff)

    # creazione dell'array per il summary
    dailySummary.append(['Calories', calTemp, calD, int((calTemp * 100) / calD)])
    dailySummary.append(['Carbohydrates', carbTemp, carbTot, int((carbTemp * 100) / carbTot)])
    dailySummary.append(['Proteins', protTemp, protTot, int((protTemp * 100) / protTot)])
    dailySummary.append(['Fats', fatTemp, fatTot, int((fatTemp * 100) / fatTot)])

    # creazione dell'array per il chart
    chartArr = [['Macro', 'Quantity']]

    carbP = int((carbTemp * 100) / carbTot)
    if carbP == 0:
        carbP = 1
    protP = int((protTemp * 100) / protTot)
    if protP == 0:
        protP = 1
    fatP = int((fatTemp * 100) / fatTot)
    if fatP == 0:
        fatP = 1

    chartArr.append(['Carbohydrates', carbP])
    chartArr.append(['Proteins', protP])
    chartArr.append(['Fats', fatP])

    userName = users_collection.find_one({'email': uEmail})['name']
    return render_template('home.html', foodArrBreakfast=foodArrBreakfast, foodArrLaunch=foodArrLaunch,
                           foodArrDinner=foodArrDinner, foodArrSnack=foodArrSnack, dailySummary=dailySummary,
                           chartArr=chartArr, userName=userName, foodDate=foodDate.strftime("%Y-%m-%d"))


# Pagina per il login
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    # Setup errore
    messageDiv = ['']

    # Ricaviamo dal post tutti i valori che ci servono per il log in
    email = request.form.get('email')
    password = request.form.get('password')

    # Controlliamo che nessun valore sia nullo, e nel caso procediamo con il controllo di email e password
    if email is not None and password is not None:

        # Verifica se c'è un utente con la mail inserita
        query = users_collection.find_one({"email": email})

        # se la query è andata a buon fine, controlliamo la password, se combaciano si effettua il log in altrimenti
        # viene passato un messaggio d'errore
        if query is not None:
            if query['password'] == password:
                flask_login.login_user(user_loader(email))
                if dailyWeight_collection.find_one({"userEmail": flask_login.current_user.id}) is None:
                    return redirect('/bodyComp')
                messageDiv = 'LoginSuccess'
            else:
                messageDiv = 'LoginError'
        else:
            messageDiv = 'LoginError'

    return render_template('login.html', divToShow=messageDiv)


# pagina del logout
@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logoutPage():
    # si effettua il logout e si viene rimandati all'inizio del sito
    flask_login.logout_user()
    return redirect("/")


# Pagina per il sign up
@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    messageDiv = ''

    # Ricaviamo dal post tutti i valori che ci servono per il sign up
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')
    sex = 'todo'
    bDate = request.form.get('date')
    height = 0
    wSport = 0
    dCal = 0
    dWat = 0
    objective = 'todo'
    objectiveW = 0
    permission = 0

    if email is not None:
        try:
            if users_collection.find_one({'email': email}) is not None:
                raise
            bDate = datetime.datetime.strptime(bDate, '%Y-%m-%d')
            if yearToday(bDate) <= 17:
                raise
            if len(password) < 8:
                raise
            insQuery = {"email": email, "password": password, "name": name, "surname": surname, "sex": sex,
                        "bDate": bDate,
                        "height": height, 'objective': objective, 'objectiveW': objectiveW, 'dCal': dCal, 'dWat': dWat,
                        "wSport": wSport,
                        "permission": permission}
            users_collection.insert_one(insQuery)
        except Exception as e:
            print(e)
            messageDiv = 'RegisterError'
            return render_template('register.html', divToShow=messageDiv)

        messageDiv = 'RegisterSuccess'
        # Carichiamo la pagina registrata con successo
        return render_template('register.html', divToShow=messageDiv)

    return render_template('register.html', divToShow=messageDiv)


# pagina per inserire i dati utente per la prima volta, succesivamente modificabili da '/profile'
@app.route('/bodyComp', methods=['GET', 'POST'])
@flask_login.login_required
def bodyCompPage():
    # Recupero dati dalla form e inizializzazione variabili
    uEmail = flask_login.current_user.id
    weight = request.form.get('weight')
    height = request.form.get('height')
    sex = request.form.get('sexRadio')
    wSport = request.form.get('wSport')
    objectiveW = request.form.get('objectiveW')

    objective = request.form.get('wRadio')

    dCal = 0
    dWat = 0

    # se non viene riscontrato nessun peso nel database
    if dailyWeight_collection.find_one({'userEmail': uEmail}) is None:
        try:
            # recuperiamo gli anni dell'utente e calcoliamo calorie e acqua giornaliere
            yearUser = yearToday(users_collection.find_one({'email': uEmail})['bDate'])
            [dWat, dCal] = watCal(sex, int(wSport), yearUser, weight, height, objective)
            dCal = int(dCal)
        except:
            # se qualcosa va storto mostriamo ancora bodyComp
            return render_template("bodyComp.html")

        try:
            # inseriamo il peso e aggiorniamo i dati dell'utente
            dailyWeight_collection.insert_one(
                {'weight': float(weight), 'day': todayDate(), 'userEmail': uEmail})
            users_collection.update_one({'email': uEmail},
                                        {"$set": {'height': int(height), 'sex': sex, 'wSport': int(wSport),
                                                  'dWat': dWat, 'dCal': dCal, 'objective': objective,
                                                  'objectiveW': int(objectiveW)}})
            # infine redirect a home
            return redirect('/home')
        except:
            # se qualcosa va storto mostriamo ancora bodyComp
            return render_template("bodyComp.html")
    else:
        # se l'utente ha già inserito un peso lo rimanda a '/weight'
        return redirect('/weight')


# pagina per l'inserimento dei cibi mangiati dall'utente
@app.route('/foodSelector', methods=['GET', 'POST'])
@flask_login.login_required
def foodSelectorPage():
    import re

    uEmail = flask_login.current_user.id
    # Recupero dati dalla form e inizializzazione variabili
    search = request.form.get('search')
    gr = request.form.get('gr')
    foodName = request.form.get('foodName')
    meal = request.form.get('meal')
    mealTemp = []
    food = []
    divToShow = ''

    # se viene ricercato un cibo viene mostrato, altrimenti viene mostrato tutto l'elenco
    if search is not None:
        search = re.compile(search, re.IGNORECASE)
        foodQr = foodList_collection.find({'name': search, 'validate': True})
    else:
        foodQr = foodList_collection.find({'validate': True}).limit(100)
    for x in foodQr:
        food.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    # se il cibo è inserito
    if foodName is not None and gr is not None:
        if len(foodName) >0 and len(gr) >0:
            # controlliamo se ha già un record con il pasto scelto
            if dailyFood_collection.find_one({'userEmail': uEmail, 'day': todayDate()}) is not None:
                try:
                    # nel caso c'è lo inseriamo in mealTemp
                    mealTemp = \
                        dailyFood_collection.find_one({'userEmail': uEmail, 'day': todayDate()})[meal]
                except:
                    # altrimenti non facciamo nulla
                    pass
                # aggiungiamo il cibo appena inserito dall'utente
                mealTemp.append([foodName, gr])
                try:
                    dailyFood_collection.update_one({'userEmail': uEmail, 'day': todayDate()},
                                                    {"$set": {meal: mealTemp}})
                    divToShow = 'foodAddSuccess'
                except:
                    divToShow = 'foodAddError'
            else:
                try:
                    # se non ha alcun record ancora veine inserito con mealTemp
                    dailyFood_collection.insert_one(
                        {'userEmail': uEmail, 'day': todayDate(), meal: mealTemp})
                    divToShow = 'foodAddSuccess'
                except:
                    divToShow = 'foodAddError'


    return render_template("foodSelector.html", foodArr=food, divToShow=divToShow)


# pagina di inserimento peso dell' utente
@app.route('/weight', methods=['GET', 'POST'])
@flask_login.login_required
def weightPage():
    # Recupero dati dalla form e inizializzazione variabili
    uEmail = flask_login.current_user.id
    weight = request.form.get('weight')
    chartData = [['Date', 'Weight', 'Goal Weight']]
    userId = users_collection.find_one({'email': uEmail})

    # se è stato passato un peso
    if weight is not None:
        try:
            # aggiorniamo quello di oggi
            dailyWeight_collection.update_one({'day': todayDate(), 'userEmail': uEmail},
                                              {'$set': {'weight': float(weight)}})
        except:
            # se non possibile inseriamo un nuovo peso
            dailyWeight_collection.insert_one(
                {'weight': float(weight), 'day': todayDate(), 'userEmail': uEmail})

    # recuperiamo tutti i pesi, se sono 0 rimandiamo a bodyComp
    rec = dailyWeight_collection.find({'userEmail': uEmail})
    if rec.count() == 0:
        return redirect('/bodyComp')

    # creiamo i dati per il chart del peso e peso obbiettivo
    for x in rec:
        chartData.append([x['day'].strftime("%d/%m/%Y"), x['weight'], userId['objectiveW']])

    # recupero ultimi dati da passare
    lastWeight = chartData[-1][1]
    gWeight = chartData[-1][2]
    return render_template('weight.html', weightArray=chartData, lastWeight=lastWeight, gWeight=gWeight,
                           lossWeight=int(chartData[1][1]) - int(lastWeight))


# pagina inserimento acqua giornaliera
@app.route('/water', methods=['GET', 'POST'])
@flask_login.login_required
def waterPage():
    # Recupero dati dalla form e inizializzazione variabili
    uEmail = flask_login.current_user.id
    water = request.form.get('mlwater')
    reset = request.form.get('reset')
    racml = users_collection.find_one({'email': uEmail})["dWat"]
    todayml = 0

    try:
        # se esiste un record riprendiamo gli ml giornalieri e li aggiorniamo
        todayml = \
            dailyWater_collection.find_one({'userEmail': uEmail, 'day': todayDate()})['ml']
        if isNumber(water):
            todayml += int(water)
        dailyWater_collection.update_one({'userEmail': uEmail, 'day': todayDate()},
                                         {"$set": {'ml': todayml}})
    except:
        # altrimenti aggiungiamo il record
        if isNumber(water):
            todayml += int(water)
        dailyWater_collection.insert_one(
            {'userEmail': uEmail, 'day': todayDate(), 'ml': todayml})

    # se reset è stato premuto allora resettiamo l'acqua di oggi
    if reset is not None:
        dailyWater_collection.delete_one({'userEmail': uEmail, 'day': todayDate()})

    return render_template('water.html', todayml=todayml, racml=racml)


# pagina per modifica dati utente e eliminazione dello stesso
@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profilePage():
    # Recupero dati dalla form e inizializzazione variabili
    uEmail = flask_login.current_user.id

    qr = users_collection.find_one({'email': uEmail})

    weight = dailyWeight_collection.find_one({'userEmail': uEmail})['weight']
    [dWat, dCal] = watCal(qr['sex'], int(qr['wSport']), yearToday(qr['bDate']), int(weight), qr['height'],
                          qr['objective'])
    users_collection.update_one({'email': uEmail}, {'$set': {'dCal': int(dCal)}})
    uName = qr['name']
    uSurname = qr['surname']
    uBDate = qr['bDate']
    uObjW = qr['objectiveW']
    uObj = qr['objective']
    uWSport = qr['wSport']
    uPass = qr['password']

    name = request.form.get('name')
    surname = request.form.get('surname')
    email = request.form.get('email')
    bDate = request.form.get('date')

    objectiveW = request.form.get('objW')
    objective = request.form.get('wRadio')
    wSport = request.form.get('wSport')

    oldPsw = request.form.get('oldPsw')
    newPsw1 = request.form.get('newPsw1')
    newPsw2 = request.form.get('newPsw2')

    delAccount = request.form.get('delAccount')
    delPass = request.form.get('delPass')

    # nel caso in cui il nome cambia lo aggiorniamo
    if name is not None:
        if len(name) > 1:
            users_collection.update_one({'email': uEmail}, {'$set': {'name': name}})
    # nel caso in cui il cognome cambia lo aggiorniamo
    if surname is not None:
        if len(name) > 1:
            users_collection.update_one({'email': uEmail}, {'$set': {'surname': surname}})
    # nel caso in cui l'email cambia la aggiorniamo
    if email is not None:
        if len(name) > 1:
            if users_collection.find_one({'email': email}) is None:
                users_collection.update_one({'email': uEmail}, {'$set': {'email': email}})

    # nel caso la data di nascita cambia l'aggiorniamo
    if bDate is not None:
        if yearToday(bDate) <= 17:
            pass
        else:
            bDate = datetime.datetime.strptime(bDate, '%Y-%m-%d')
            users_collection.update_one({'email': uEmail}, {'$set': {'bDate': bDate}})

    # controlli per modifica password
    if oldPsw == uPass:
        if newPsw1 is not None:
            if len(newPsw1) >= 8:
                if newPsw1 == newPsw2:
                    users_collection.update_one({'email': uEmail}, {'$set': {'password': newPsw1}})
    # nel caso in cui l'obbiettivo di peso cambia lo modifichiamo
    if objectiveW is not None:
        if isNumber(objectiveW):
            users_collection.update_one({'email': uEmail}, {'$set': {'objectiveW': int(objectiveW)}})

    # nel caso in cui l'obbiettivo cambia lo modifichiamo
    if objective is not None:
        if objective != uObj:
            users_collection.update_one({'email': uEmail}, {'$set': {'objective': objective}})

    # nel caso in cui lo sport settimanale cambia lo modifichiamo
    if wSport is not None:
        if wSport != uWSport:
            users_collection.update_one({'email': uEmail}, {'$set': {'wSport': int(wSport)}})

    # controlli per eliminare l'account e successivo svuotamento dal database
    if delAccount is not None:
        if delPass == uPass:
            users_collection.delete_many({'email': uEmail})
            dailyWeight_collection.delete_many({'userEmail': uEmail})
            dailyWater_collection.delete_many({'userEmail': uEmail})
            dailyFood_collection.delete_many({'userEmail': uEmail})
            return redirect('/logout')
    return render_template('profile.html', uEmail=uEmail, uName=uName, uSurname=uSurname, uObjW=uObjW, date=uBDate.strftime("%Y-%m-%d"))


# pagina per l'inserimento degli alimenti
@app.route('/addFood', methods=['GET', 'POST'])
@flask_login.login_required
def addFoodPage():
    # Recupero dati dalla form e inizializzazione variabili
    name = request.form.get('foodName')
    cal = request.form.get('foodCal')
    carb = request.form.get('foodCarb')
    protein = request.form.get('foodProt')
    fat = request.form.get('foodFat')
    validate = False

    try:
        if foodList_collection.find_one({'name': name}):
            raise
        foodList_collection.insert_one(
            {'name': name, 'cal': int(cal), 'carb': int(carb), 'protein': int(protein), 'fat': int(fat),
             'validate': validate})
        divToShow = 'foodAddSuccess'
    except:
        # se non riusciamo rimandiamo alla stessa pagina
        return render_template('addFood.html')
    return render_template('addFood.html', divToShow=divToShow)


# pagina admin per verifica del cibo inserito dall'utente
@app.route('/admin', methods=['GET', 'POST'])
@flask_login.login_required
def adminPage():
    import re

    # Recupero dati dalla form e inizializzazione variabili
    uEmail = flask_login.current_user.id

    # se l'utente non ha i permessi fingiamo la pagina '/admin' non esista
    if users_collection.find_one({'email': uEmail})["permission"] == 0:
        return render_template('404.html')

    searchTV = request.form.get('searchTV')
    search = request.form.get('search')

    verified = request.form.get('verified')
    delete = request.form.get('delete')
    foodArrTV = []
    foodArr = []

    # nel caso si prema il pulsante per verificare aggiorniamo l'alimento con il validate=true
    if verified is not None:
        foodList_collection.update_one({'name': verified, 'validate': False}, {"$set": {'validate': True}})
    # nel caso si prema il pulsante per eliminare l'alimento esso viene eliminato
    if delete is not None:
        foodList_collection.delete_one({'name': delete, 'validate': False})

    # pulsante di ricerca per i cibi da validare
    if searchTV is not None:
        searchTV = re.compile(searchTV, re.IGNORECASE)
        foodQr = foodList_collection.find({'name': searchTV, 'validate': False})
    else:
        foodQr = foodList_collection.find({'validate': False}).limit(100)
    for x in foodQr:
        foodArrTV.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    # pulsante di ricerca per i cibi verificati
    if search is not None:
        search = re.compile(search, re.IGNORECASE)
        foodQr = foodList_collection.find({'name': search, 'validate': True})
    else:
        foodQr = foodList_collection.find({'validate': True}).limit(100)
    for x in foodQr:
        foodArr.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    return render_template('admin.html', foodArrTV=foodArrTV, foodArr=foodArr)


# Handler per le pagine non trovate
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


# funzione per trasferire i dati scalati dal record del cibo di oggi ad un array
def foodArrDump(dailyMeal, meal):
    foodArr = []
    try:
        dailyMeal[meal]
    except:
        return foodArr
    for food in dailyMeal[meal]:
        qr = foodList_collection.find({'name': food[0]})
        grCf = int(food[1]) / 100
        for x in qr:
            foodArr.append(
                [x["name"], food[1], int((x["cal"] * grCf)), int((x["carb"] * grCf)), int((x["protein"] * grCf)),
                 int((x["fat"] * grCf))])
    return foodArr
