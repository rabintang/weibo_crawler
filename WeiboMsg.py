#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import csv
import utility
import logging
from WeiboDB import WeiboDB

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboMsg:
	def __init__(self):		
		self.wbdb = WeiboDB();

	# 获取用户信息前的初始化
	def init_user(self, uid = None):
		self.weibomsg = {
			#'uid':'',	#用户的id
			'un':'',	#用户用户名
			'iu':'',	#用户头像URL
			'mid':'',	#消息id
			'mc':'',	#消息内容
			'nc':'',	#消息中@的用户
			'run':'',	#转发的消息的用户名
			'rmc':'',	#转发的消息的内容
			'pu':'',	#消息中的图片
			'rrc':'',	#转发的消息的转发次数
			'rcc':'',	#转发的消息的评论次数
			'rpage':'',	#转发的消息的微博页面
			'rpt':'',	#转发的消息的发布时间
			'rc':'0',	#消息的转发次数
			'cc':'0',	#消息的评论次数
			'srn':'',	#消息来源
			'page':'',	#消息的微博页面
			'pt':''		#消息的发布时间
		}
		self.flag = 0		# 标记是否第一条记录,因为csv文件要在第一条记录前写标签
		self.flag_un = 0	# 标记是否已经获得用户名
		self.uid = uid;

	# 处理一个分页的微博数据,需要继续处理返回True,停止处理返回False
	def get_content(self, content):
		self.content = content
		#self.weibomsg['uid'] = str(self.uid)	#后加的用户id
		self.pos = 0
		if self.flag_un == 0:
			self.get_weiboun()
			self.get_weiboiu()
			self.flag_un = 1
		while self.pos >= 0:
			# 每次应该初始化一下
			self.init_weibo()
			try:
				self.get_weibomid()
			except Exception,e:
				logging.exception('%s get_weibomid: ' + str(e), self.uid);
				continue;
			if(self.wbdb.is_stop(self.weibomsg['mid'])):
				return False;
			if self.pos == -1:
				break
			try:
				self.get_weibomc()
			except Exception,e:
				logging.exception('%s get_weibomc: ' + str(e), self.uid);
				continue;
			try:
				self.get_retweet_info()
			except Exception,e:
				logging.exception('%s get_retweet_info: ' + str(e) , self.uid);
				continue;
			try:
				self.get_weibopu()
			except Exception, e:
				logging.exception('%s get_weibopu: ' + str(e), self.uid);
				continue;
			try:
				self.get_weiborc()
			except Exception,e:				
				logging.exception('%s get_weiborc: ' + str(e), self.uid);
				continue;
			try:
				self.get_weibocc()
			except Exception,e:				
				logging.exception('%s get_weibocc: ' + str(e), self.uid);
				continue;
			try:
				self.get_weibo_page_pt()
			except Exception,e:				
				logging.exception('%s get_weibo_page_pt: ' + str(e), self.uid);
				continue;
			try:
				self.get_weibo_srn()
			except Exception,e:				
				logging.exception('%s get_weibo_page_pt: ' + str(e), self.uid);
				continue;
			#self.outputInfo();
			self.wbdb.combine_klg(self.uid, self.weibomsg);
			if( utility.time_exceed(self.weibomsg['pt']) ):
				return False;
		return True;

	def init_weibo(self):
		self.weibomsg['run'] = ''
		self.weibomsg['rmc'] = ''
		self.weibomsg['pu'] = ''
		self.weibomsg['rrc'] = ''
		self.weibomsg['rcc'] = ''
		self.weibomsg['rpage'] = ''
		self.weibomsg['rpt'] = ''
		self.weibomsg['srn'] = ''

	# 将一条微博记录写到csv文件
	def writeResult(self):
		#filename = './data/'+self.uid+'-'+self.weibomsg['un']+'.csv'
		filename = './data/' + self.uid + '.csv'
		#utility.iprint('filename: '+filename)
		writer = csv.writer(file(filename,'a'))
		if self.flag == 0:
			writer.writerow(['un','iu','mid','mc','run','rmc','pu','rrc','rcc','rpage','rpt','rc','cc','page','pt'])
			self.flag = 1
		writer.writerow((self.weibomsg['un'],self.weibomsg['iu'],self.weibomsg['mid'],self.weibomsg['mc'],
			self.weibomsg['run'],self.weibomsg['rmc'],self.weibomsg['pu'],self.weibomsg['rrc'],self.weibomsg['rcc'],
			self.weibomsg['rpage'],self.weibomsg['rpt'],self.weibomsg['rc'],self.weibomsg['cc'],self.weibomsg['page'],
			self.weibomsg['pt']))
	
	# 去除content中的标签
	def eraseTag(self,content):	
		pos = content.find('<')
		while pos != -1:
			end = content.find('>')+1
			if end<pos:
				end = content.find('>',end)+1
				if end == 0:
					break
			strold = content[pos:end]
			content = content.replace(strold,'')
			pos = content.find('<')
			#print content
		return content
	
	# 输出微博信息到屏幕
	def outputInfo(self):
		print 'iu  is :' + self.weibomsg['iu']
		print 'un  is :' + self.weibomsg['un']
		print 'mid is :' + self.weibomsg['mid']
		print 'mc  is :' + self.weibomsg['mc']
		print 'nc  is :' + self.weibomsg['nc']
		print 'run is :' + self.weibomsg['run']
		print 'rmc is :' + self.weibomsg['rmc']
		print 'pu  is :' + self.weibomsg['pu']
		print 'rrc is :' + self.weibomsg['rrc']
		print 'rcc is :' + self.weibomsg['rcc']
		print 'rpt is :' + self.weibomsg['rpt']
		print 'rpage is :' + self.weibomsg['rpage'];
		print 'rc  is :' + self.weibomsg['rc']
		print 'cc  is :' + self.weibomsg['cc']
		print 'page is :' + self.weibomsg['page'];
		print 'pt  is :' + self.weibomsg['pt']
		print 'srn is :' + self.weibomsg['srn'];
		print '======================================'
		#time.sleep(1)