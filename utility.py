# -*- coding: utf-8 -*-

import time
from datetime import datetime
from datetime import timedelta
import os
import csv
import platform
import sys
import WeiboDB
import GlobalVal as GV

reload(sys)
sys.setdefaultencoding('utf-8')

#获取系统当前时间
def now():
    return time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))

#格式化时间
def time_format(origin):
    year = time.strftime('%Y',time.localtime(time.time()));
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()));
    now = datetime.now();

    if( origin.find('今天') != -1 ):
        format = date + origin[2:];
    elif( origin.find('分钟前') != -1 ):
        minus = int(origin[0:-3]) * -1;
        minus = timedelta(minutes=minus);
        format = datetime.now() + minus;
        format = format.strftime('%Y-%m-%d %H:%M');
    elif( origin.find('月') != -1 ):
        end = origin.find('月');
        month = origin[0:end];
        begin = end + 3;
        end = origin.find('日');
        day = origin[begin:end];
        format = year + '-' + month + '-' + day + origin[end+3:];
    else:
        format = origin;
    return format;

# 是否超过时间间隔
def time_exceed(time, interval = -15):
    date_time = datetime.strptime(time,'%Y-%m-%d %H:%M');
    earlist_day = datetime.now() + timedelta(days=interval);
    if( earlist_day > date_time ):
        return True;
    return False;

#字符串是否只含空白
def isEmpty(text):
    text = text.replace(' ','').replace('\n','').replace('\t','')
    if len(text) == 0:
        return True
    return False

#清除数据中的空白及斜杆
def clearSpace(text):
    text = text.replace('\r\n','').replace('\n','').replace('\t','').replace('\\/','/')
    text = text.strip();
    return text

#创建文件夹路径
def createDirs(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except:
        print 'directory',path,'created error'
        return False
    return True

#创建文件
def createFile(path,name):
    try:
        if path[len(path)-1] != '/':
            path = path + '/'
        filePath = path + name
        if not os.path.exists(filePath):            
            if not createDirs(path):
                return None
        f = open(filePath,'w')
        return f
    except:
        print 'file',filePath,'created error'
        return None
		
#以操作系统默认编码打印字符串,参数str的编码为utf-8
def iprint(str):
	sysstr = platform.system()
	if(sysstr =="Windows"):
		print str.decode('utf-8').encode('gbk')
	else:
		print str

# 判断一个字符串中是否存在某个词条,存在返回词条ID列表,否则返回空集
def match_klg(text):
    text = clear_noise(text).lower();
    key_list = [];
    for key in GV.dict_klg.keys():
        pos = text.find(key);
        while( pos != -1 ):
            # 判断匹配到的字符的左边
            if( pos != 0 ):
                left = key[0];
                if( is_en_char(left) and is_en_char(text[pos-1]) ): # key的最左边是字母,其左边一个字符也是字母
                    pos = text.find(key, pos + len(key));
                    continue;
            # 判断匹配到字符位置的右边
            if( pos + len(key) < len(text) ):
                right = key[len(key)-1];
                if( is_en_char(right) and is_en_char(text[pos+len(key)]) ): # key的最右边是字母,其右边一个字符也是字母
                    pos = text.find(key, pos + len(key));
                    continue;
            key_list.append(GV.dict_klg[key]);
            break;
    return key_list;

# 是否数字
def is_number(i):
    return 0x0030<=ord(i)<=0x0039;

# 是否英文字母
def is_en_char(i):
    return ( 0x0041<=ord(i)<=0x005a ) or ( 0x0061<=ord(i)<=0x007a );

# 是否中文字符
def is_cn_char(i):
    return 0x4e00<=ord(i)<=0x9fa5;

# 匹配词条之前清理微博
def clear_noise(msg):
    if( not isinstance(msg, unicode) ):
        msg = unicode(msg, 'utf-8');

    # 去除@用户
    stop_flag = [' ', ':', ',','：',];
    tag = '@';
    pos = msg.find(tag);
    while( pos != -1):
        new = msg[:pos];
        for i in range(pos+len(tag), len(msg)):
            if(msg[i] in stop_flag):
                new += ' ' + msg[i+1:];
                msg = new;
                break;
        if(i == len(msg) - 1):
            msg = new;
        pos = msg.find(tag);

    # 去掉超链接
    stop_flag = [' ', ','];
    tag = 'http://';
    pos = msg.find(tag);
    while( pos != -1):
        new = msg[:pos];
        for i in range(pos+len(tag), len(msg)):
            if( msg[i] in stop_flag or is_cn_char(msg[i]) ):
                new += " " + msg[i:];
                msg = new;
                break;
        if(i == len(msg) - 1):
            msg = new;
        pos = msg.find(tag);

    return msg;
    #return msg.encode('utf-8');

if __name__ == '__main__':
    db = WeiboDB.WeiboDB();
    result = db.select("SELECT mc FROM weibomsg");
    for row in result:
        print clear_noise(row[0]);
        #print type(row[0]);
        raw_input();