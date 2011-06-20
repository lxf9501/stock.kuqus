# -*- encoding:utf-8 -*-
from flask import Flask, render_template
from stock import app, connection, utils
from stock.models import DayEntry
import datetime
import pymongo

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/stock/<stock_code>')
def stock_show(stock_code):
    day_data = stock_day_data(stock_code)
    min5_data = stock_min5_data(stock_code)
    week_data = stock_week_data(stock_code)
    month_data = stock_month_data(stock_code)
    min30_data = stock_min30_data(stock_code)
    min60_data = stock_min60_data(stock_code)
    return render_template('candle.html', day_data=day_data, min5_data=min5_data, week_data=week_data, month_data=month_data, min30_data=min30_data, min60_data=min60_data)

def stock_day_data(stock_code):
    stock_days = connection.stock.stock_day.find({'code':stock_code}).sort('date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['name'] = ' '
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['dates'] = []
    for r in stock_days:
    	stock['open_prices'].insert(0, round(r['open'],2))
    	stock['close_prices'].insert(0, round(r['close'],2))
    	stock['high_prices'].insert(0, round(r['high'],2))
    	stock['low_prices'].insert(0, round(r['low'],2))
    	stock['dates'].insert(0, r['date'].strftime('%y-%m-%d'))	
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_day.find({'code':stock_code},{'close':1}).sort('date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
    	close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)	
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)	
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)
    return stock	

@app.route('/stock/min5/<stock_code>')
def stock_min5(stock_code):
    min5_data = stock_min5_data(stock_code)
    return render_template('candle_min5.html', min5_data=min5_data)
    
def stock_min5_data(stock_code):
    stock_min5 = connection.stock.stock_min5.find({'code':stock_code}).sort('date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['dates'] = []
    for r in stock_min5:
    	stock['open_prices'].insert(0, round(r['open'],2))
    	stock['close_prices'].insert(0, round(r['close'],2))
    	stock['high_prices'].insert(0, round(r['high'],2))
    	stock['low_prices'].insert(0, round(r['low'],2))
    	stock['dates'].insert(0, r['date'].strftime('%y-%m-%d'))	
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_min5.find({'code':stock_code},{'close':1}).sort('date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
    	close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)	
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)	
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)	
    return stock

@app.route('/stock/week/<stock_code>')
def stock_week(stock_code):
    stock_data = stock_week_data(stock_code)
    return render_template('candle_week.html', stock_data=stock_data)
    
def stock_week_data(stock_code):
    stock_week = connection.stock.stock_week.find({'code':stock_code}).sort('start_date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['start_dates'] = []
    stock['end_dates'] = []
    for r in stock_week:
        stock['open_prices'].insert(0, round(r['open'],2))
        stock['close_prices'].insert(0, round(r['close'],2))
        stock['high_prices'].insert(0, round(r['high'],2))
        stock['low_prices'].insert(0, round(r['low'],2))
        stock['start_dates'].insert(0, r['start_date'].strftime('%y-%m-%d'))    
        stock['end_dates'].insert(0, r['end_date'].strftime('%y-%m-%d'))    
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_week.find({'code':stock_code},{'close':1}).sort('start_date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
        close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)    
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)    
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)    
    return stock

@app.route('/stock/month/<stock_code>')
def stock_week(stock_code):
    stock_data = stock_month_data(stock_code)
    return render_template('candle_month.html', stock_data=stock_data)
    
def stock_month_data(stock_code):
    stock_month = connection.stock.stock_month.find({'code':stock_code}).sort('start_date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['start_dates'] = []
    stock['end_dates'] = []
    for r in stock_month:
        stock['open_prices'].insert(0, round(r['open'],2))
        stock['close_prices'].insert(0, round(r['close'],2))
        stock['high_prices'].insert(0, round(r['high'],2))
        stock['low_prices'].insert(0, round(r['low'],2))
        stock['start_dates'].insert(0, r['start_date'].strftime('%y-%m-%d'))    
        stock['end_dates'].insert(0, r['end_date'].strftime('%y-%m-%d'))    
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_month.find({'code':stock_code},{'close':1}).sort('start_date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
        close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)    
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)    
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)    
    return stock

@app.route('/stock/min30/<stock_code>')
def stock_min30(stock_code):
    stock_data = stock_min30_data(stock_code)
    return render_template('candle_min30.html', stock_data=stock_data)
    
def stock_min30_data(stock_code):
    stock_min30 = connection.stock.stock_min30.find({'code':stock_code}).sort('start_date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['start_dates'] = []
    stock['end_dates'] = []
    for r in stock_min30:
        stock['open_prices'].insert(0, round(r['open'],2))
        stock['close_prices'].insert(0, round(r['close'],2))
        stock['high_prices'].insert(0, round(r['high'],2))
        stock['low_prices'].insert(0, round(r['low'],2))
        stock['start_dates'].insert(0, r['start_date'].strftime('%y-%m-%d'))    
        stock['end_dates'].insert(0, r['end_date'].strftime('%y-%m-%d'))    
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_min30.find({'code':stock_code},{'close':1}).sort('start_date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
        close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)    
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)    
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)    
    return stock

@app.route('/stock/min60/<stock_code>')
def stock_min60(stock_code):
    stock_data = stock_min60_data(stock_code)
    return render_template('candle_min60.html', stock_data=stock_data)
    
def stock_min60_data(stock_code):
    stock_min60 = connection.stock.stock_min60.find({'code':stock_code}).sort('start_date', pymongo.DESCENDING).limit(100)
    stock = {}
    stock['code'] = stock_code
    stock['open_prices'] = []
    stock['close_prices'] = []
    stock['high_prices'] = []
    stock['low_prices'] = []
    stock['start_dates'] = []
    stock['end_dates'] = []
    for r in stock_min60:
        stock['open_prices'].insert(0, round(r['open'],2))
        stock['close_prices'].insert(0, round(r['close'],2))
        stock['high_prices'].insert(0, round(r['high'],2))
        stock['low_prices'].insert(0, round(r['low'],2))
        stock['start_dates'].insert(0, r['start_date'].strftime('%y-%m-%d'))    
        stock['end_dates'].insert(0, r['end_date'].strftime('%y-%m-%d'))    
        stock['min_price'] = min(stock['low_prices'])
        stock['max_price'] = max(stock['high_prices'])
    close_rs = connection.stock.stock_min60.find({'code':stock_code},{'close':1}).sort('start_date', pymongo.DESCENDING).limit(100 + 30)
    close_list = []
    for r in close_rs:
        close_list.append(r['close'])
    stock['ma_5'] = utils.ma_av(close_list, 100, 5)    
    stock['ma_10'] = utils.ma_av(close_list, 100, 10)    
    stock['ma_30'] = utils.ma_av(close_list, 100, 30)    
    return stock

if __name__ == '__main__':
    app.run(debug=True)
