from flask import Flask

app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vinay2001@localhost/flkproject'
app.config['SECRET_KEY']="SRUNNSIILT"
app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
UPLOAD_FOLDER = 'app/static/files/'
ALLOWED_EXTENSIONS = {'doc', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = {'.doc', '.pdf'}
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 20

from app import routes
from app.database import db,migrate

