#!/usr/bin/python
#-*- coding: utf-8 -*-

import logging
from DBHelper import DBHelper
import sys
import utility
import GlobalVal as GV

reload(sys)   
sys.setdefaultencoding('utf8')

class WeiboDB:
	def __init__(self):
		self.db = DBHelper(GV.server, GV.user, GV.pwd, GV.database);

	# 将微博与词条进行关联操作.执行失败返回 False, 否则返回 True
	def combine_klg(self, uid, weibomsg):
		if(weibomsg['run'] != ''):
			text = weibomsg['mc'] + "//@" + weibomsg['run'] + weibomsg['rmc'];
		else:
			text = weibomsg['mc'];

		klg_list = utility.match_klg(text);
		if( len(klg_list) > 0 ): # 存在某个词条
			try:
				insert_batch = [];
				update_mt = '';
				for klg in klg_list:
					insert_batch.append( [weibomsg['mid'], klg] );
					update_mt += str(klg) + ',';
				update_mt = update_mt.rstrip(',');
				self.db.insert("INSERT IGNORE INTO weibomsg (mid,uid,un,sn,iu,mc,murl,srn,iurl,rc,cc,pt,nc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
					[weibomsg['mid'], uid, weibomsg['un'], weibomsg['un'], weibomsg['iu'], text, weibomsg['page'], 
					weibomsg['srn'], weibomsg['pu'], weibomsg['rc'], weibomsg['cc'], weibomsg['pt'], weibomsg['nc']]);
				self.db.insert_many("INSERT IGNORE INTO abbre_weibomsg (mid,abrid) VALUES(%s, %s)", insert_batch);
				self.db.update("UPDATE `abbreviation` SET mt=%s WHERE abrid IN (" + update_mt + ")", [utility.now()]);
			except Exception,e:
				logging.exception("%s 绑定数据库失败: " + str(e), weibomsg['mid']);


	# 是否停止采集该用户余下微博,是则返回 True,否则返回 False
	def is_stop(self, mid):
		res = self.db.select_one("SELECT COUNT(*) FROM `weibomsg` WHERE mid='%s'" % mid);
		if(res and res[0] > 0):
			return True;
		return False;

	def select(self, query):
		return self.db.select(query);