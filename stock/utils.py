# -*- encoding:utf-8 -*-
from __future__ import division

def ma_av(datas, day_count, av_count):
    ma_av_list = []
    for i in range(day_count):
	tmp = datas[i:av_count + i]
	act_count = len(tmp)
	total = 0
	av_total = 0
	if act_count >= 1:
	    for x in tmp:
	        total = total + x
	    av_total = round(total / act_count, 2)
	ma_av_list.insert(0, av_total)
    return ma_av_list

if __name__ == '__main__':
    datas = [1,2,3,4,5,6,7,8,9]
    print datas
    print ma_av(datas, 10, 111)
