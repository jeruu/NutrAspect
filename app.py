from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route('/eeee', methods=['GET', 'POST'])
def fromProvaStampa():  # put application's code here
    ris = 'email'
    return ris


@app.route('/', methods=['GET', 'POST'])
def fromProva():
    #data = request.data()
    email = request.form.get('email')
    password = request.form.get('password')
    ris = 'email ' + str(email) + ' ' + 'password ' + str(password)
    print(request.data)
    if email == 'secondogg@libero.it':
        return fromProvaStampa()

    #print(data)
    return  render_template('index.html')





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
