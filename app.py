from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route('/fx', methods=['GET', 'POST'])
def fromProvaStampa(email):  # put application's code here

    return ''' <h1>{} <- email :D <h1> '''.format(email)


@app.route('/', methods=['GET', 'POST'])
def fromProva():
    #data = request.data()
    email = request.form.get('email')
    password = request.form.get('password')
    ris = 'email ' + str(email) + ' ' + 'password ' + str(password)
    print(request.data)
    if email == 'secondogg@libero.it':
        return fromProvaStampa(email)

    #print(data)
    return  render_template('index.html')





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
