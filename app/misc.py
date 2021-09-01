import datetime
import json
from bson import ObjectId

def yearToday(bDate):
    today = datetime.datetime.today()
    if bDate.month <= today.month:
        if bDate.day <= today.day:
            return int(today.year - bDate.year)
    return int(today.year - bDate.year) - 1


def todayDate():
    dt = datetime.datetime.today()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def isNumber(number):
    try:
        int(number)
        return True
    except:
        return False


def watCal(sex, wSport, yearUser, weight, height, objective):
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

# funzione per riempire la collezione partendo dal json
def fillCollection(collection, path, datename):
    # apriamo il file in modalità lettura
    tFile = open(path, 'r')

    #trasformiamo il file in un json
    tData = json.load(tFile)

    # per ogni record in tData
    for u in tData:
        # riconvertiamo l'id e gestiamo la data e inserimento
        u['_id'] = ObjectId(u['_id']['$oid'])
        if datename is not None:
            u[datename]['$date'] = u[datename]['$date'][:-14]
            u[datename] = datetime.datetime.strptime(u[datename]['$date'], '%Y-%m-%d')
        try:
            collection.insert_one(u)
        except:
            pass


# funzione per trasferire i dati scalati dal record del cibo di oggi ad un array
def foodArrDump(collection,dailyMeal, meal):
    foodArr = []
    try:
        dailyMeal[meal]
    except:
        return foodArr
    for food in dailyMeal[meal]:
        qr = collection.find({'name': food[0]})
        grCf = int(food[1]) / 100
        for x in qr:
            foodArr.append(
                [x["name"], food[1], int((x["cal"] * grCf)), int((x["carb"] * grCf)), int((x["protein"] * grCf)),
                 int((x["fat"] * grCf))])
    return foodArr