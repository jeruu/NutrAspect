import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
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


@app.route('/cls', methods=['GET', 'POST'])
def puliscituttooo():
    dailyWater_collection.delete_many({})
    dailyWeight_collection.delete_many({})
    users_collection.delete_many({})
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def homeProva():
    return render_template('home.html')


# franc
class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user


# Pagina per il login
@app.route('/login', methods=['GET', 'POST'])
def loginNuovo():
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


# TODO LOGIN NUOVO


@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logoutNuovo():
    flask_login.logout_user()
    return 'loguoutfatto'


# Pagina per il sign up
@app.route('/register', methods=['GET', 'POST'])
def registerProva():
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
                        "height": height, 'objective': objective, 'dCal': dCal, 'dWat': dWat, "wSport": wSport,
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
def bodyCompProva():
    weight = request.form.get('weight')
    height = request.form.get('height')
    sex = request.form.get('sexRadio')
    wSport = request.form.get('wSport')

    objective = request.form.get('wRadio')

    dCal = 0
    dWat = 0
    if dailyWeight_collection.find_one({'userEmail': flask_login.current_user.id}) is None:
        yearUser = yearToday(users_collection.find_one({'email': flask_login.current_user.id})['bDate'])
        try:
            yearUser = yearToday(users_collection.find_one({'email': flask_login.current_user.id})['bDate'])
            [dWat, dCal] = calWat(sex, int(wSport), yearUser, weight, height, objective)
            dCal = int(dCal)
        except Exception as e:
            print(e)
            return render_template("bodyComp.html")

        try:
            dailyWeight_collection.insert_one(
                {'weight': float(weight), 'day': todayDate(), 'userEmail': flask_login.current_user.id})
            users_collection.update_one({'email': flask_login.current_user.id},
                                        {"$set": {'height': int(height), 'sex': sex, 'wSport': int(wSport),
                                                  'dWat': dWat, 'dCal': dCal, 'objective': objective}})
            return redirect('/home')
        except Exception as e:
            print(e)
            return render_template("bodyComp.html")
    else:
        return redirect('/protected/weight')


@app.route('/foodSelector', methods=['GET', 'POST'])
def foodSelectorProva():
    return render_template("foodSelector.html")


@app.route('/protected/weight', methods=['GET', 'POST'])
@flask_login.login_required
def weightProva():
    import html
    weight = request.form.get('weight')
    chartData = [['Date', 'Weight']]
    if weight is not None:
        userId = users_collection.find_one({'email': flask_login.current_user.id})
        dailyWeight_collection.insert_one(
            {'weight': float(weight), 'day': todayDate(), 'userEmail': flask_login.current_user.id})

    rec = dailyWeight_collection.find({'userEmail': flask_login.current_user.id})
    for x in rec:
        chartData.append([x['day'].strftime("%d/%m/%Y"), x['weight']])
    print(chartData)

    return render_template('weight.html', weightArray=html.unescape(chartData))


# Handler per le pagine non trovate
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run()


@app.route('/water', methods=['GET', 'POST'])
def waterprova():
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


def yearToday(bDate):
    today = datetime.datetime.today()
    if bDate.month <= today.month:
        if bDate.day <= today.day:
            return int(today.year - bDate.year)
    return int(today.year - bDate.year) - 1


def todayDate():
    dt = datetime.datetime.today()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def isNumber(water):
    try:
        int(water)
        return True
    except:
        return False


def calWat(sex, wSport, yearUser, weight, height, objective):
    dWat = 0
    dCal = 0
    if sex == 'male':
        dWat = 2800
        dCal = int(66.5 + (13.75 * float(weight)) + (5 * int(height)) - (6.775 * int(yearUser)))
    else:
        dWat = 2000
        dCal = int(65.5 + (9.563 * float(weight)) + (1.850 * int(height)) - (4.676 * int(yearUser)))

    if wSport == 0:
        dCal *= 1.2
    else:
        if wSport == 1 or wSport == 2:
            dCal *= 1.375
        else:
            if wSport == 3 or wSport == 4:
                dCal *= 1.50
            else:
                if wSport == 5:
                    dCal *= 1.725
                else:
                    dCal *= 1.9
    if objective == 'wLoss':
        dCal -= (dCal * 17) / 100
    if objective == 'wGain':
        dCal += 500
    return [dWat, dCal]
