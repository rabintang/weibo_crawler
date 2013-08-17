#!/usr/bin/python
# -*- coding: utf-8 -*-

import weiboLogin
import urllib
import urllib2
import time
import os
import getWeiboPage
import threading
from WeiboDB import WeiboDB
import logging
import utility
import GlobalVal as GV
mylock = threading.RLock()
   
class worker(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self);
		self.t_name = name;
		self.thread_stop = False;

	def run(self):
		global task_list;

		WBcontent = getWeiboPage.getWeiboPage();
		while not GV.task_list.empty() and not self.thread_stop:
			uid = GV.task_list.get();
			utility.iprint( "还剩下 %d 个任务" % GV.task_list.qsize() );
			if uid:
				WBcontent.set_uid(uid);
				utility.iprint( 'Thread %s handle id:%s'%(self.t_name, WBcontent.get_uid()) );
				try:
					WBcontent.get_msg(WBcontent.get_uid());
				except Exception, e:					
					logging.exception("%s 用户信息解析出错:" + str(e), WBcontent.get_uid());
					continue;

	def stop(self):
		self.thread_stop = True;

def test():
	WBcontent = getWeiboPage.getWeiboPage(GV.dict_klg);
	while not GV.task_list.empty():
		uid = GV.task_list.get();
		utility.iprint( "还剩下 %d 个任务" % GV.task_list.qsize() );
		if uid:
			WBcontent.set_uid(uid);
			utility.iprint( 'handle id:%s'%WBcontent.get_uid() );
			try:
				WBcontent.get_msg(WBcontent.get_uid());
			except Exception, e:
				logging.exception(uid + "用户信息解析出错: " + str(e));
				continue;

def controller():
	num = input('input threads number:')
	for i in range(1, num+1):
		worker('T'+str(i)).start()

	while True:
		time.sleep(60);
		count = threading.activeCount();
		utility.iprint( '还有 %d 个活动线程'%count );
		if(count < num and not GV.task_list.empty()):
			for j in range(count-1, num):
				 worker('T' + str(j)).start();
		elif(GV.task_list.empty() and count <= 1):
			break;

def init():
	# 配置日志
	# '[%(asctime)s]-%(levelname)s : %(message)s'
	logging.basicConfig(filename='weibo.log',filemode='a',format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',level=logging.DEBUG)

	# 进行模拟登录
	filename = './config/account'#保存微博账号的用户名和密码，第一行为用户名，第二行为密码
	WBLogin = weiboLogin.weiboLogin()
	if WBLogin.login(filename)==1:
		print 'Login success!'
	else:
		print 'Login error!'
		exit()
	
	db = WeiboDB();
	# 构造知识词条字典
	abr_list = db.select("SELECT abrid, kl FROM `abbreviation`");
	for abr in abr_list:
		GV.dict_klg[abr[1]] = abr[0];

	#for abr in dict_klg.keys():
	#	print abr + ' ' + str(dict_klg[abr]);

	# 生成任务
	dict_user = {};
	user_list = db.select("SELECT uid, fui FROM `userlist`");
	for item in user_list:
		dict_user[item[0]] = 1;
		uid_list = item[1].strip("'").split("','");
		for uid in uid_list:
			dict_user[uid] = 1;
	for uid in dict_user.keys():
		GV.task_list.put(uid);
	#task_list.put('715545693');
	#task_list.put('1069205631');
	#task_list.put('1649173367');

	# 开始执行任务
	controller();
	#test();

def setLogger():  
	# 创建一个logger,可以考虑如何将它封装  
	logger = logging.getLogger('mylogger')  
	logger.setLevel(logging.DEBUG)

	# 创建一个handler，用于写入日志文件  
	fh = logging.FileHandler(os.path.join(os.getcwd(), 'log.txt'))  
	fh.setLevel(logging.DEBUG)

	# 再创建一个handler，用于输出到控制台
	ch = logging.StreamHandler()  
	ch.setLevel(logging.DEBUG)

	# 定义handler的输出格式  
	formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s')  
	fh.setFormatter(formatter)  
	ch.setFormatter(formatter)

	# 给logger添加handler  
	logger.addHandler(fh)  
	logger.addHandler(ch)

	return logger  

def test_exist_key():
	db = WeiboDB();
	# 构造知识词条字典
	abr_list = db.select("SELECT abrid, kl FROM `abbreviation`");
	for abr in abr_list:
		GV.dict_klg[abr[1].lower()] = abr[0];

	weibo_list = db.select("SELECT mc FROM weibomsg");
	#weibomsg = 'fusion io的iops已经过百万了，在wikipedia排名第一 //@TRS肖诗斌: 昨天测试了华为二代SSD，4K随机读，IOPS超过13W，吞吐量超过800M，已经大大超过fusionio卡， 还有性能更优越的华为三代SSD年底就要发布。这些证明只要专注和努力，国人同样可以作出好东西。其实SSD最好的是OCZ，读写达到1.4G/s, 华	HelloDBA出品：《Fusionio性能测试与瓶颈分析》，http://t.cn/a9Ts2j，如果你懒得看测试数据，直接看结论吧。';
	for weibomsg in weibo_list:
		key_list = utility.exist_key(weibomsg[0]);
		if( len(key_list) > 0 ):
			print weibomsg[0];
			for id in key_list:
				for key in GV.dict_klg.keys():
					if(id == GV.dict_klg[key]):
						print key;
			raw_input();

if __name__== '__main__':
    init();
    #test_exist_key();