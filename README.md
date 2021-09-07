<p align="center">
    <img src="https://github.com/jeruu/NutrAspect/blob/master/app/static/images/leaf.png?raw=true" alt="Logo image"/>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/license-Apache%202-blue" alt="Apache License 2.0 Image"/>
    <img src="https://img.shields.io/badge/university project-red" alt="University Project Image"/>
</p>

# NutrAspect

NutrAspect is a small **Web App** used to help you to track your weight by taking in consideration several aspects.
It keeps tracking of your daily calories intake and your macros. NutrAspect will help people reaching their goal and 
living a better lifestyle.<br>
This is a university project made for the 2021 edition of Web Technology (Tecnologie Web) course at the
[*Università degli Studi di Napoli Parthenope*](https://github.com/uniparthenope).

| :exclamation:  This project was made for learning purposes only. It should not replace a professional |
|-------------------------------------------------------------------------------------------------------|



# Get Started

First, you have to choose if you want to load the server and the Mongo Database using Docker or hosting it locally.

For doing so you need to change beforehand, into the `app.py`, the value `IS_LOCAL` (line 14) to `true` if you want to host it
locally or change it into `false` if you want to use the Docker instance.

Both methods will be shown below.

## Docker method

Requirements: [*Docker*](https://docs.docker.com/get-docker/), `IS_LOCAL = false`

First, we need to pull the official **Mongo Docker image** by running the following command

```bash
docker pull mongo
```

After, we have to build a multi-container Docker application by using the Docker tool **Compose**

```bash
docker-compose up --build
```

You are now ready to go! Simply open your browser and connect to the IP shown in the console and have fun.

If you're interested in **accessing the database**, you need to run the following commands

```bash
docker exec -it nutraspect_app_1 bash
```

and then

```bash
mongo --port 27017  --authenticationDatabase "admin" -u "admin" -p "admin"
```

You now have access to the database!

## Local method

Requirements: [*MongoDB Community Server*](https://www.mongodb.com/try/download/community), `IS_LOCAL = true`

Simply run the 'wsgi.py' and then open your browser and connect to [localhost:5000](http://localhost:5000)

# Technologies

The technologies that we used to build this web app are the following:

- HTML
- CSS3
- JavaScript
- Python (Flask)
- MongoDB (Community Edition)
- Docker

# Open source components

The list of open source components we used and their authors:

- Flask (licensed under the [BSD 3-Clause "New" or "Revised" License](https://github.com/pallets/flask/blob/main/LICENSE.rst))
- Bootstrap (licensed under the [MIT License](https://github.com/twbs/bootstrap/blob/main/LICENSE))
- Google Charts (licensed under the [Apache License](https://github.com/GoogleWebComponents/google-chart/blob/master/LICENSE))
- Flask Login (licensed under the [MIT License](https://github.com/maxcountryman/flask-login/blob/main/LICENSE))
- PyMongo (licensed under the [MIT License](https://github.com/mongodb/mongo-python-driver/blob/master/LICENSE))

## Assets

The list of the assets we used and their authors:

- */app/static/images/favicons/* made from [realfavicongenerator](https://realfavicongenerator.net/)
- */app/static/images/logo.png, /app/static/images/* made with [Adobe Spark](https://spark.adobe.com/it-IT/sp/)
- */app/static/css/style.css (.glass and .water)* made by [Mike Marcacci](http://jsfiddle.net/mike_marcacci/XztTN/)

## Authors

The authors of NutrAspect are:

- Porcelli Fabio [@fabio7150](https://github.com/fabio7150)
- Sannino Ciro [@jeruu](https://github.com/jeruu?tab=repositories)

