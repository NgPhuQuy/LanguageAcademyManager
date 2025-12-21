from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.config["SECRET_KEY"] = "KNJBJku f<j ]f2;w]r[jnofpmc,snKZD l12sa,lm2njwqd"
from urllib.parse import quote
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@127.0.0.1:2005/lamdb?charset=utf8mb4' % quote('*mai27082005*')
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:npq24102005@localhost/lamdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 12
app.config["SCORES"] = 3
app.config["MAX_STUDENTS_PER_COURSE"] = 25
app.config["TOTAL_SESSION_PER_COURSE"] = 8
cloudinary.config(cloud_name='dtvg4cpoq',
                  api_key='211564137488191',
                  api_secret='otiD0T9BFzzg9UyKGcTb6MHi3Ow')

login = LoginManager(app)

db = SQLAlchemy(app)
