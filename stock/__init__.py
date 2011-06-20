# -*- encoding:utf-8 -*-
import os
from flask import Flask
from stock import settings
from mongokit import Connection

app = Flask(__name__)

app.config.from_object(settings)

connection = Connection(app.config['MONGODB_HOST'],
			app.config['MONGODB_PORT'])

import views
