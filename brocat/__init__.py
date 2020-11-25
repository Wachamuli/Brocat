from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = r'b$2b$12$j7IQog.NYRWgjfRB4j5Fxu'

import brocat.views