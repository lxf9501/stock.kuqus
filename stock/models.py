# -*- encoding:utf-8 -*-
from mongokit import Document
import datetime

from stock import connection

@connection.register
class DayEntry(Document):
    __database__ = 'stock'
    __collection__ = 'stock_day'
    structure = {
	'code':unicode,
	'date':datetime.datetime,
	'open':float,
	'high':float,
	'low':float,
	'close':float,
	'vol':long,
	'day_amt':float
    }
    required_fields = ['code', 'date']
