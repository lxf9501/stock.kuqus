# -*- coding: utf-8 -*-

import os
import struct
import datetime
import pymongo
import time
import calendar

def import_stock_data(db_table, file, type):
    rs = db_table.find().sort('date', pymongo.DESCENDING).limit(1)
    max_time = None
    for r in rs:
        max_time = r['date']
    print 'max_time %s' % max_time
    file.read(4)
    (x,x,stocknum,x,x) = struct.unpack('IIIII', file.read(4*5))
    print stocknum
    stocklist = []
    for num in range(stocknum):
    	stockmap = {}
	(name, count) = struct.unpack('<10sI', file.read(10+4))
        stockmap['code'] = name
	stockmap['count'] = count
	stockmap['offets'] = struct.unpack('h'*25, file.read(25*2))
	stocklist.append(stockmap)
    
    act_insert_count = 0
    unpackstring='I'+'f'* 6 + 'HH'
    for stock in stocklist:
	code = stock['code']
	count = stock['count']
        offets = stock['offets']
        for offets_index in offets:
	    if offets_index < 0:
		continue
            start_seek = 0x41000 + offets_index * 32 * 256
	    file.seek(start_seek)
	    for i in range(256):
    	        ret = struct.unpack(unpackstring, file.read(32))
    	        t_day = datetime.datetime(1970,1,1,0,0,0) + datetime.timedelta(seconds=ret[0])
                if (max_time is not None) and (t_day <= max_time):
	            count = count - 1
                    if count == 0:
		        break
                    continue
	        open_price = round(ret[1], 2)
	        high_price = round(ret[2], 2)
                low_price = round(ret[3], 2)
	        close_price = round(ret[4], 2)
	        vol = ret[5]
	        day_amt = ret[6]
	        record = {'code': code,
		    'date': t_day,
		    'open': open_price,
		    'high': high_price,
		    'low': low_price,
		    'close': close_price,
		    'vol': vol,
		    'day_amt': day_amt,
		    'type': type}
                if (max_time is None) or (not exist(db_table, t_day, code)):
	            db_table.insert(record)
                    act_insert_count += 1
	        count -= 1
                if count == 0:
		    break
    print 'act_insert_count : %d' % act_insert_count

def exist(db_table, time, code):
    record = db_table.find_one({'date': time, 'code': code})
    return record is not None

def import_stock_week_data(db):
    db_table_day = db['stock_day']
    db_table_week = db.stock_week
    rs = db_table_week.find().sort('end_date', pymongo.DESCENDING).limit(1)
    max_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
    for r in rs:
        max_time = r['end_date']
    act_insert_count = 0
    act_update_count = 0
    #code_list = db_table_day.distinct('code')
    code_list = ['000001']
    for code in code_list:
        rs = db_table_day.find({'code': code, 'date': {'$gt': max_time}}).sort('date')
        for r in rs:
            r_date = r['date']
            r_date_monday =  r_date - datetime.timedelta(days= (r_date.weekday()))
            r_date_sunday = r_date_monday + datetime.timedelta(days= 6)
            fit_week_data = db_table_week.find_one({'code': '000001', 'start_date': {'$gte': r_date_monday, '$lte': r_date_sunday}})

            if fit_week_data is not None:
                update_week_data = {}
                update_week_data['end_date'] = r_date
                update_week_data['close'] = r['close']
                update_week_data['high'] = max(fit_week_data['high'], r['high'])
                update_week_data['low'] = min(fit_week_data['low'], r['low'])
                update_week_data['day_count'] = fit_week_data['day_count'] +  1
                update_week_data['vol'] = fit_week_data['vol'] + r['vol']
                update_week_data['week_amt'] = fit_week_data['week_amt'] + r['day_amt']
                db_table_week.update({'_id': fit_week_data['_id']}, {'$set': update_week_data})
                act_update_count += 1
            else:
                fit_week_data = {}
                fit_week_data['start_date'] = r_date
                fit_week_data['end_date'] = r_date
                fit_week_data['open'] = r['open']
                fit_week_data['close'] = r['close']
                fit_week_data['high'] = r['high']
                fit_week_data['low'] = r['low']
                fit_week_data['day_count'] = 1
                fit_week_data['vol'] = r['vol']
                fit_week_data['week_amt'] = r['day_amt']
                fit_week_data['type'] = r['type']
                fit_week_data['code'] = r['code']
                db_table_week.save(fit_week_data)
                act_insert_count += 1
    print 'act_insert_count %d -- act_update_count %d' % (act_insert_count, act_update_count)
    
def import_stock_month_data(db):
    db_table_day = db['stock_day']
    db_table_month = db.stock_month
    rs = db_table_month.find().sort('end_date', pymongo.DESCENDING).limit(1)
    max_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
    for r in rs:
        max_time = r['end_date']
    
    act_insert_count = 0
    act_update_count = 0
    #code_list = db_table_day.distinct('code')
    code_list = ['000001']
    for code in code_list:
        rs = db_table_day.find({'code': code, 'date': {'$gt': max_time}}).sort('date')
        for r in rs:
            r_date = r['date']
            r_date_first =  datetime.datetime(r_date.year, r_date.month, 1)
            r_date_last = datetime.datetime(r_date.year, r_date.month, calendar.monthrange(r_date.year, r_date.month)[1])
            fit_month_data = db_table_month.find_one({'code': code, 'start_date': {'$gte': r_date_first, '$lte': r_date_last}})
            if fit_month_data is not None:
                update_month_data = {}
                update_month_data['end_date'] = r_date
                update_month_data['close'] = r['close']
                update_month_data['high'] = max(fit_month_data['high'], r['high'])
                update_month_data['low'] = min(fit_month_data['low'], r['low'])
                update_month_data['day_count'] = fit_month_data['day_count'] +  1
                update_month_data['vol'] = fit_month_data['vol'] + r['vol']
                update_month_data['month_amt'] = fit_month_data['month_amt'] + r['day_amt']
                db_table_month.update({'_id': fit_month_data['_id']}, {'$set': update_month_data})
                act_update_count += 1
            else:
                fit_month_data = {}
                fit_month_data['start_date'] = r_date
                fit_month_data['end_date'] = r_date
                fit_month_data['open'] = r['open']
                fit_month_data['close'] = r['close']
                fit_month_data['high'] = r['high']
                fit_month_data['low'] = r['low']
                fit_month_data['day_count'] = 1
                fit_month_data['vol'] = r['vol']
                fit_month_data['month_amt'] = r['day_amt']
                fit_month_data['type'] = r['type']
                fit_month_data['code'] = r['code']
                db_table_month.save(fit_month_data)
                act_insert_count += 1
    print 'act_insert_count %d -- act_update_count %d' % (act_insert_count, act_update_count)

def import_stock_min30_data(db):
    db_table_min5 = db.stock_min5
    db_table_min30 = db.stock_min30
    rs = db_table_min30.find().sort('end_date', pymongo.DESCENDING).limit(1)
    max_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
    for r in rs:
        max_time = r['end_date']
    
    act_insert_count = 0
    act_update_count = 0
    #code_list = db_table_min5.distinct('code')
    code_list = ['000001']
    for code in code_list:
        rs = db_table_min5.find({'code': code, 'date': {'$gt': max_time}}).sort('date')
        for r in rs:
            r_date = r['date']
            hour_sep = 0
            first_minute = 1
            last_minute = 30
            first_hour = r_date.hour
            last_hour = r_date.hour
            if r_date.minute > 30:
                first_minute = 31
                last_minute = 0
                last_hour = r_date.hour + 1
            if r_date.minute == 0:
                first_minute = 31
                last_minute = 0
                first_hour = r_date.hour - 1
            r_date_first =  datetime.datetime(r_date.year, r_date.month, r_date.day, first_hour, first_minute)
            r_date_last =  datetime.datetime(r_date.year, r_date.month, r_date.day, last_hour, last_minute)
            fit_min30_data = db_table_min30.find_one({'code': code, 'start_date': {'$gte': r_date_first, '$lte': r_date_last}})
            if fit_min30_data is not None:
                update_min30_data = {}
                update_min30_data['end_date'] = r_date
                update_min30_data['close'] = r['close']
                update_min30_data['high'] = max(fit_min30_data['high'], r['high'])
                update_min30_data['low'] = min(fit_min30_data['low'], r['low'])
                update_min30_data['count'] = fit_min30_data['count'] +  1
                update_min30_data['vol'] = fit_min30_data['vol'] + r['vol']
                update_min30_data['amt'] = fit_min30_data['amt'] + r['day_amt']
                db_table_min30.update({'_id': fit_min30_data['_id']}, {'$set': update_min30_data})
                act_update_count += 1
            else:
                fit_min30_data = {}
                fit_min30_data['start_date'] = r_date
                fit_min30_data['end_date'] = r_date
                fit_min30_data['open'] = r['open']
                fit_min30_data['close'] = r['close']
                fit_min30_data['high'] = r['high']
                fit_min30_data['low'] = r['low']
                fit_min30_data['count'] = 1
                fit_min30_data['vol'] = r['vol']
                fit_min30_data['amt'] = r['day_amt']
                fit_min30_data['type'] = r['type']
                fit_min30_data['code'] = r['code']
                db_table_min30.save(fit_min30_data)
                act_insert_count += 1
    print 'act_insert_count %d -- act_update_count %d' % (act_insert_count, act_update_count)

def import_stock_min60_data(db):
    table_min30 = db.stock_min30
    table_min60 = db.stock_min60
    act_insert_count = 0
    code_list = table_min30.distinct('code')
    for code in code_list:
        rs = table_min60.find({'code': code}).sort('end_date', pymongo.DESCENDING).limit(1)
        max_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        for r in rs:
            max_time = r['end_date']
        rs = table_min30.find({'code': code, 'start_date': {'$gt': max_time}}).sort('start_date')
        index = 0
        current_min60_record = {}
        for r in rs:
            start_hour = r['start_date'].hour
            start_minute = r['start_date'].minute
            is_hour_start = False
            if start_hour == 9 and start_minute == 35:
                is_hour_start = True
            elif start_hour == 10 and start_minute == 35:
                is_hour_start = True
            elif start_hour == 13 and start_minute == 5:
                is_hour_start = True
            elif start_hour == 14 and start_minute == 5:
                is_hour_start = True
            if index == 0 and not is_hour_start:
                print 'skip %s' % r
                index += 1
                continue 
            if is_hour_start:
                current_min60_record = {}
                current_min60_record['start_date'] = r['start_date']
                current_min60_record['open'] = r['open']
                current_min60_record['high'] = r['high']
                current_min60_record['low'] = r['low']
                current_min60_record['vol'] = r['vol']
                current_min60_record['amt'] = r['amt']
                current_min60_record['type'] = r['type']
                current_min60_record['code'] = r['code']
            else:
                current_min60_record['end_date'] = r['end_date']
                current_min60_record['close'] = r['close']
                current_min60_record['high'] = max(current_min60_record['high'], r['high'])
                current_min60_record['low'] = min(current_min60_record['low'], r['low'])
                current_min60_record['vol'] += r['vol']
                current_min60_record['amt'] += r['amt']
                table_min60.save(current_min60_record) 
                act_insert_count += 1   
    print 'act_insert_count %d ' % act_insert_count

def check_min30_data(db):
    table = db.stock_min30
    code_list = table.distinct('code')
    for code in code_list:
        rs = table.find({'code': code}).sort('start_date', pymongo.ASCENDING).limit(1)
        first_record = None
        for r in rs:
            first_record = r
            break
        if first_record is not None and first_record['start_date'].minute != 5 and first_record['start_date'].minute != 35:
            table.remove({'_id': first_record['_id']})       
    
if __name__ == '__main__':
    con = pymongo.Connection('localhost', 27017)
    db = con['stock']
    db_table_day = db['stock_day']
    '''
    print 'start import sh day.dat'
    f = open('/Users/alan/work/gs/dzh/2011-06-18/sh/DAY.DAT', 'rb')
    import_stock_data(db_table_day, f, 'sh')
    f.close()
    '''
    
    print '\nstart import week data' 
    #db.stock_week.remove()
    #import_stock_week_data(db)

    print '\nstart import month data' 
    #db.stock_month.remove()
    #import_stock_month_data(db)

    db_table_min5 = db['stock_min5']
    print '\nstart import sh min5.dat'
    f = open('/Users/alan/work/gs/dzh/2011-06-18/sh/MIN.DAT', 'rb')
    #import_stock_data(db_table_min5, f, 'sh')
    f.close()

    print '\nstart import min30 data'
    #db.stock_min30.remove()
    #import_stock_min30_data(db)

    print '\nstart import min60 data'
    db.stock_min60.remove()
    import_stock_min60_data(db)
    
    print '\nstart check min30 data'
    #check_min30_data(db)
