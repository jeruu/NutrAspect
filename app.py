import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from fitness import *

import flask_login
import pymongo

# assegnazione app
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

if __name__ == '__main__':
    app.run()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user


# todo index
@app.route('/', methods=['GET', 'POST'])
def indexPage():
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
@flask_login.login_required
def homePage():
    dailyMeal = dailyFood_collection.find_one({'userEmail': flask_login.current_user.id, 'day': todayDate()})
    dailySummary = []

    calTemp = 0
    carbTemp = 0
    protTemp = 0
    fatTemp = 0

    carbCoeff = .4 / 4
    protCoeff = .3 / 4
    fatCoeff = .3 / 9

    foodArrBreakfast = foodArrDump(dailyMeal, 'Breakfast')
    foodArrLaunch = foodArrDump(dailyMeal, 'Launch')
    foodArrDinner = foodArrDump(dailyMeal, 'Dinner')
    foodArrSnack = foodArrDump(dailyMeal, 'Snack')

    # TODO
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

    calD = int(users_collection.find_one({'email': flask_login.current_user.id})['dCal'])
    carbTot = int(calD * carbCoeff)
    protTot = int(calD * protCoeff)
    fatTot = int(calD * fatCoeff)

    dailySummary.append(['Calories', calTemp, calD, int((calTemp * 100) / calD)])
    dailySummary.append(['Carbohydrates', carbTemp, carbTot, int((carbTemp * 100) / carbTot)])
    dailySummary.append(['Proteins', protTemp, protTot, int((protTemp * 100) / protTot)])
    dailySummary.append(['Fats', fatTemp, fatTot, int((fatTemp * 100) / fatTot)])

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

    print(foodArrSnack)
    userName = users_collection.find_one({'email': flask_login.current_user.id})['name']
    return render_template('home.html', foodArrBreakfast=foodArrBreakfast, foodArrLaunch=foodArrLaunch,
                           foodArrDinner=foodArrDinner, foodArrSnack=foodArrSnack, dailySummary=dailySummary,
                           chartArr=chartArr, userName=userName)


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

        # todo eliminare
        print('POST pieno')
        print(email)
        print(password)

        # Verifica se c'è un utente con la mail inserita
        query = users_collection.find_one({"email": email})

        # todo eliminare
        print(query)

        # se la query è andata a buon fine, controlliamo la password, se combaciano si effettua il log in
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

    # altrimenti todo
    else:
        print('POST vuoto')

    return render_template('login.html', divToShow=messageDiv)


@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logoutPage():
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
            if yearToday(bDate) <= 0:
                raise
            insQuery = {"email": email, "password": password, "name": name, "surname": surname, "sex": sex,
                        "bDate": bDate,
                        "height": height, 'objective': objective, 'objectiveW': objectiveW, 'dCal': dCal, 'dWat': dWat,
                        "wSport": wSport,
                        "permission": permission}
            users_collection.insert_one(insQuery)
        except:
            messageDiv = 'RegisterError'
            return render_template('register.html', divToShow=messageDiv)

        messageDiv = 'RegisterSuccess'
        # Carichiamo la pagina registrata con successo
        return render_template('register.html', divToShow=messageDiv)

    return render_template('register.html', divToShow='')


@app.route('/bodyComp', methods=['GET', 'POST'])
@flask_login.login_required
def bodyCompPage():
    weight = request.form.get('weight')
    height = request.form.get('height')
    sex = request.form.get('sexRadio')
    wSport = request.form.get('wSport')
    objectiveW = request.form.get('objectiveW')

    objective = request.form.get('wRadio')

    dCal = 0
    dWat = 0
    if dailyWeight_collection.find_one({'userEmail': flask_login.current_user.id}) is None:
        try:
            yearUser = yearToday(users_collection.find_one({'email': flask_login.current_user.id})['bDate'])
            [dWat, dCal] = watCal(sex, int(wSport), yearUser, weight, height, objective)
            dCal = int(dCal)
        except Exception as e:
            print(e)
            return render_template("bodyComp.html")

        try:
            dailyWeight_collection.insert_one(
                {'weight': float(weight), 'day': todayDate(), 'userEmail': flask_login.current_user.id})
            users_collection.update_one({'email': flask_login.current_user.id},
                                        {"$set": {'height': int(height), 'sex': sex, 'wSport': int(wSport),
                                                  'dWat': dWat, 'dCal': dCal, 'objective': objective,
                                                  'objectiveW': int(objectiveW)}})
            return redirect('/home')
        except Exception as e:
            print(e)
            return render_template("bodyComp.html")
    else:
        return redirect('/weight')


@app.route('/foodSelector', methods=['GET', 'POST'])
@flask_login.login_required
def foodSelectorPage():
    search = request.form.get('search')
    gr = request.form.get('gr')
    foodName = request.form.get('foodName')
    meal = request.form.get('meal')
    mealTemp = []
    food = []
    divToShow = ''

    if search is not None:
        foodQr = foodList_collection.find({'name': search, 'validate': True})
    else:
        foodQr = foodList_collection.find({'validate': True})
    for x in foodQr:
        food.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    if foodName is not None and gr is not None:
        if dailyFood_collection.find_one({'userEmail': flask_login.current_user.id, 'day': todayDate()}) is not None:
            try:
                mealTemp = \
                    dailyFood_collection.find_one({'userEmail': flask_login.current_user.id, 'day': todayDate()})[meal]
            except:
                pass

            mealTemp.append([foodName, gr])
            dailyFood_collection.update_one({'userEmail': flask_login.current_user.id, 'day': todayDate()},
                                            {"$set": {meal: mealTemp}})
        else:
            dailyFood_collection.insert_one(
                {'userEmail': flask_login.current_user.id, 'day': todayDate(), meal: mealTemp})
        divToShow = 'foodAddSuccess'

    return render_template("foodSelector.html", foodArr=food, divToShow=divToShow)


@app.route('/weight', methods=['GET', 'POST'])
@flask_login.login_required
def weightPage():
    weight = request.form.get('weight')
    chartData = [['Date', 'Weight', 'Goal Weight']]
    userId = users_collection.find_one({'email': flask_login.current_user.id})
    if weight is not None:
        try:
            dailyWeight_collection.update_one({'day': todayDate(), 'userEmail': flask_login.current_user.id},
                                              {'$set': {'weight': float(weight)}})
        except:
            dailyWeight_collection.insert_one(
                {'weight': float(weight), 'day': todayDate(), 'userEmail': flask_login.current_user.id})

    rec = dailyWeight_collection.find({'userEmail': flask_login.current_user.id})
    if rec.count() == 0:
        return redirect('/bodyComp')

    for x in rec:
        chartData.append([x['day'].strftime("%d/%m/%Y"), x['weight'], userId['objectiveW']])

    lastWeight = chartData[-1][1]
    gWeight = chartData[-1][2]
    return render_template('weight.html', weightArray=chartData, lastWeight=lastWeight, gWeight=gWeight,
                           lossWeight=chartData[1][1] - lastWeight)


@app.route('/water', methods=['GET', 'POST'])
@flask_login.login_required
def waterPage():
    water = request.form.get('mlwater')
    reset = request.form.get('reset')
    racml = users_collection.find_one({'email': flask_login.current_user.id})["dWat"]
    todayml = 0

    try:
        todayml = \
            dailyWater_collection.find_one({'userEmail': flask_login.current_user.id, 'day': todayDate()})['ml']
        if isNumber(water):
            todayml += int(water)
        dailyWater_collection.update_one({'userEmail': flask_login.current_user.id, 'day': todayDate()},
                                         {"$set": {'ml': todayml}})
    except:
        if isNumber(water):
            todayml += int(water)
        dailyWater_collection.insert_one(
            {'userEmail': flask_login.current_user.id, 'day': todayDate(), 'ml': todayml})

    if reset is not None:
        dailyWater_collection.delete_one({'userEmail': flask_login.current_user.id, 'day': todayDate()})

    return render_template('water.html', todayml=todayml, racml=racml)


@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profilePage():
    uEmail = flask_login.current_user.id

    qr = users_collection.find_one({'email': uEmail})

    weight = dailyWeight_collection.find_one({'userEmail': uEmail})['weight']
    [dWat, dCal] = watCal(qr['sex'], int(qr['wSport']), yearToday(qr['bDate']), int(weight), qr['height'],
                          qr['objective'])
    users_collection.update_one({'email': uEmail}, {'$set': {'dCal': int(dCal)}})
    print(dCal)
    uName = qr['name']
    uSurname = qr['surname']
    uObjW = qr['objectiveW']
    uObj = qr['objective']
    uWSport = qr['wSport']

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

    if name is not None:
        if len(name) > 1:
            users_collection.update_one({'email': uEmail}, {'$set': {'name': name}})
    if surname is not None:
        if len(name) > 1:
            users_collection.update_one({'email': uEmail}, {'$set': {'surname': surname}})
    if email is not None:
        if len(name) > 1:
            if users_collection.find_one({'email': email}) is None:
                users_collection.update_one({'email': uEmail}, {'$set': {'email': email}})
    # if bDate is not None:
    #    users_collection.update_one({'email': uEmail}, {'$set': {'bDate': bDate}})

    if oldPsw == qr['password']:
        if newPsw1 is not None:
            if len(newPsw1) > 6:
                if newPsw1 == newPsw2:
                    users_collection.update_one({'email': uEmail}, {'$set': {'password': newPsw1}})
    if objectiveW is not None:
        if isNumber(objectiveW):
            users_collection.update_one({'email': uEmail}, {'$set': {'objectiveW': int(objectiveW)}})

    if objective is not None:
        if objective != uObj:
            users_collection.update_one({'email': uEmail}, {'$set': {'objective': objective}})

    if wSport is not None:
        if wSport != uWSport:
            users_collection.update_one({'email': uEmail}, {'$set': {'wSport': int(wSport)}})

    return render_template('profile.html', uEmail=uEmail, uName=uName, uSurname=uSurname, uObjW=uObjW)


@app.route('/addFood', methods=['GET', 'POST'])
@flask_login.login_required
def addFoodPage():
    name = request.form.get('foodName')
    cal = request.form.get('foodCal')
    carb = request.form.get('foodCarb')
    protein = request.form.get('foodProt')
    fat = request.form.get('foodFat')
    validate = False
    try:
        foodList_collection.insert_one(
            {'name': name, 'cal': int(cal), 'carb': int(carb), 'protein': int(protein), 'fat': int(fat),
             'validate': validate})
        divToShow = 'foodAddSuccess'
    except:
        return render_template('addFood.html')
    return render_template('addFood.html', divToShow=divToShow)


@app.route('/admin', methods=['GET', 'POST'])
@flask_login.login_required
def adminPage():
    if users_collection.find_one({'email': flask_login.current_user.id})["permission"] == 0:
        return render_template('404.html')

    searchTV = request.form.get('searchTV')
    search = request.form.get('search')

    verified = request.form.get('verified')
    delete = request.form.get('delete')
    foodArrTV = []
    foodArr = []

    # TODO BOTTONIX
    if verified is not None:
        foodList_collection.update_one({'name': verified, 'validate': False}, {"$set": {'validate': True}})
    if delete is not None:
        foodList_collection.delete_one({'name': delete, 'validate': False})

    if searchTV is not None:
        foodQr = foodList_collection.find({'name': searchTV, 'validate': False})
    else:
        foodQr = foodList_collection.find({'validate': False})
    for x in foodQr:
        foodArrTV.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    if search is not None:
        foodQr = foodList_collection.find({'name': search, 'validate': True})
    else:
        foodQr = foodList_collection.find({'validate': True})
    for x in foodQr:
        foodArr.append([x["name"], x["cal"], x["carb"], x["protein"], x["fat"]])

    return render_template('admin.html', foodArrTV=foodArrTV, foodArr=foodArr)


# Handler per le pagine non trovate
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


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
