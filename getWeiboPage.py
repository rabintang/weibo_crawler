#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import sys
import time
import CommonWeiboMsg
import CompanyWeiboMsg
import OfficeWeiboMsg
import utility
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

class getWeiboPage:	
	def __init__(self):
		self.charset = 'utf-8'
		self.page_num = 1		# 微博总共有多少页
		self.flag = 0			# 标记是否已经获取页数
		self.num = 0			# 标记一页中的第几分页
		self.version = -1;		# 微博的版本(普通用户版0, 企业用户版1, 新浪官方版2)
		self.comm_wbmsg = CommonWeiboMsg.CommonWeiboMsg();
		self.comp_wbmsg = CompanyWeiboMsg.CompanyWeiboMsg();
		self.offi_wbmsg = OfficeWeiboMsg.OfficeWeiboMsg();
		self.wbmsg = None;

	# 为微博解析选择版本
	def select_version(self):
		if(self.version == 0):
			self.comm_wbmsg.init_user(self.uid);
			self.wbmsg = self.comm_wbmsg;
		elif(self.version == 1):
			self.comp_wbmsg.init_user(self.uid);
			self.wbmsg = self.comp_wbmsg;
		elif(self.version == 2):
			self.offi_wbmsg.init_user(self.uid);
			self.wbmsg = self.offi_wbmsg;
		else:
			self.wbmsg = None;

	def set_uid(self,puid):
		self.uid = puid

	def get_uid(self):
		return self.uid

	# 预处理,包括:获取page_id,选择微博解析类型,微博总页数.成功返回True,否则返回False
	def preprocess(self, uid):
		# 获取 page_id	
		self.body = {
			'__rnd':'',
			'_k':'',
			'_t':'0',
			'count':'15',
			'end_id':'',
			'max_id':'',
			'page':1,
			'pagebar':'',
			'pre_page':'0',
			'uid':uid
		};
		url = 'http://weibo.com/u/' + uid + '?profile_ftype=1';
		content = self.download(url);		
		if( content == None ):
			logging.info('%s 页面加载失败', url);
			return False;
		tag = "$CONFIG['page_id']='";
		pos1 = content.find(tag) + len(tag);
		if( pos1 == -1):
			logging.info('%s page_id解析失败', uid);
			return False;
		pos2 = content.find("'", pos1);
		self.page_id = content[pos1:pos2];

		# 获取微博总页数,以及版本选择
		if(not self.get_totallpage_num(content, uid)): #微博总页数获取失败
			logging.info('%s 微博总页数解析失败', uid);
			return False;
		self.select_version();

		# 设置页面url加载的参数
		self.body = {
			'is_search':'0',
			'visible':'0',
			'is_tag':'0',
			'profile_ftype':1,
			'pagebar':'',
			'pre_page':'0',
			'page':1
		};
		return True;

	# 处理一个 uid 的微博知识
	def get_msg(self, uid):
		self.flag = 0
		self.uid = uid;
		if( not self.preprocess(uid) ):
			return;
		url = self.get_url()
		for i in range(1, self.page_num+1):
			self.body['page'] = i			
			if( not self.get_firstpage(url, uid) ):
				break;
			if( not self.get_secondpage(url, uid) ):
				break;
			if( not self.get_thirdpage(url, uid) ):
				break;

	# 判断用户是否存在,存在返回True,否则返回False
	def user_exist(self, content):
		if(content.find('<title>错误提示') != -1):
			return False;
		return True;

	# 获取新浪官方微博总数,成功返回True,否则返回False
	def totalpage_office(self, content):
		pos1 = content.find('<table class="W_tc"');
		if( pos1 != -1 ):
			pos2 = content.find('<\/table>', pos1);
			if(pos2 != -1):
				slug = content[pos1:pos2];
				bTag = 'mod=weibo"><strong class="">';
				pos1 = slug.find(bTag) + len(bTag);
				pos2 = slug.find('<\/strong>', pos1);
				temp = slug[pos1:pos2];
				if(temp.isdigit()):
					self.page_num = int(temp);
					return True;
		return False;

	# 获取企业用户微博总数,成功返回True,否则返回False
	def totalpage_company(self, content):
		pos1 = content.find('class="user_atten clearfix">');
		if( pos1 != -1):
			pos2 = content.find('<\/ul>', pos1);
			if(pos2 != -1):
				slug = content[pos1:pos2];
				eTag = '<\/strong><span>微博';
				pos2 = slug.find(eTag);
				if(pos2 != -1):
					bTag = '<strong>';
					pos1 = slug.rfind(bTag, 0, pos2);
					if(pos1 != -1):
						pos1 = pos1 + len(bTag);
						temp = slug[pos1:pos2];
						if(temp.isdigit()):
							self.page_num = int(temp);
							return True;
		return False;

	# 获取一般用户微博总数,成功返回True,否则返回False
	def totalpage_common(self, content):
		tag1 = '<strong node-type="weibo">'
		pos1 = content.find(tag1)+len(tag1)
		tag2 = '<\/strong>'
		pos2 = content.find(tag2,pos1)
		temp = content[pos1:pos2]
		if(temp.isdigit()):
			self.page_num = int(temp);
			return True;
		return False;

	# 获取微博页面的总页数,成功True,否则返回False
	def get_totallpage_num(self, content, uid):
		version = -1;
		try:
			if(self.user_exist(content)):
				if(not self.totalpage_common(content)):
					if(not self.totalpage_company(content)):
						if(not self.totalpage_office(content)):
							logging.warning('%s 无法解析微博总页数', uid);
							self.version = -1;
							return False;
						else:
							self.version = 2;
							#return False;
					else:
						self.version = 1;
				else:
					self.version = 0;
			else:
				logging.info('%s 用户不存在', uid);
				return False;
		except Exception,e:
			logging.exception("%s 获取总页数失败: " + str(e), uid);
			writer = utility.createFile('error', uid);
			writer.write(content);
			writer.close();
			return False;

		self.page_num = self.page_num / 45 + 1
		utility.iprint( self.get_uid() + ':微博总共有 ' + str(self.page_num) + ' 页' )
		logging.info(uid + " 共有 %d 页微博", self.page_num);
		return True;

	# 获取第一分页微博,不用继续处理后续微博返回False
	def get_firstpage(self, url, uid):
		self.body['pre_page'] = self.body['page']-1
		self.num = 1	
		content = self.download(url)
		if( content == None ):
			return True;
		return self.wbmsg.get_content(content)
	
	# 获取第二分页微博,不用继续处理后续微博返回False
	def get_secondpage(self, url, uid):
		self.body['count'] = '15'
		self.body['pagebar'] = '0'
		self.body['pre_page'] = self.body['page']
		self.num = 2
		content = self.download(url)
		if(content == None):
			return True;
		return self.wbmsg.get_content(content)
		
	# 获取第三分页微博,不用继续处理后续微博返回False
	def get_thirdpage(self, url, uid):
		self.body['count'] = '15'
		self.body['pagebar'] = '1'
		self.body['pre_page'] = self.body['page']
		self.num = 3
		content = self.download(url);
		if(content == None):
			return True;
		result = self.wbmsg.get_content(content)
		utility.iprint(self.get_uid() + ':获取第' + str(self.body['page']) + '页微博成功')
		return result;
	
	# 获取用户微博页面的url
	def get_url(self):
		url = 'http://weibo.com/p/' + self.page_id + '/';
		if( self.version == 0):
			url += 'weibo?';
		else:
			url += 'mblog?';
		return url

	# 下载网页,并进行解码,编码
	def download(self, url):
		try:
			url = url + urllib.urlencode(self.body)
			req = urllib2.Request(url)
			result = urllib2.urlopen(req)
			text = result.read()
		except Exception, e:
			logging.error('%s 网页下载失败: ' + str(e), url);
			return None;
		try:
			content = text.decode(self.charset, 'ignore');
			content = eval("u'''" + content + "'''").encode(self.charset);
		except Exception, e:
			logging.error('%s 网页解码失败: ' + str(e), url);
			return None;
		return content


if __name__ == '__main__':
	#getWeiboPage = getWeiboPage();
	pass;