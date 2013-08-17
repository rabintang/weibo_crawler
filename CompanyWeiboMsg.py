#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import utility
import logging
from WeiboDB import WeiboDB
from WeiboMsg import WeiboMsg

reload(sys)
sys.setdefaultencoding('utf-8')

class CompanyWeiboMsg(WeiboMsg):
	def __init__(self):
		WeiboMsg.__init__(self);
	
	# 获取用户名(un)
	def get_weiboun(self):
		self.pos = 0
		tag = '<a class="logo_img"';
		pos = self.content.find(tag, self.pos);
		if(pos != -1):
			bTag = 'title="';
			eTag = '"';
			pos1 = self.content.find(bTag, pos) + len(bTag);
			pos2 = self.content.find(eTag, pos1);
			self.weibomsg['un'] = self.content[pos1:pos2].strip()
			self.pos = pos2;
	
	# 获取用户头像image url(iu)
	def get_weiboiu(self):
		bTag = 'src="';
		eTag = '"';
		pos1 = self.content.find(bTag, self.pos) + len(bTag)
		pos2 = self.content.find(eTag, pos1)
		self.weibomsg['iu'] = self.content[pos1:pos2].replace('\\','')
		self.pos = pos2
	
	# 获得微博id(mid)
	def get_weibomid(self):
		tag = 'action-type="feed_list_item"'
		self.pos = self.content.find(tag,self.pos) # self.pos 定位当前处理微博的游标所在地
		if self.pos != -1:
			bTag = 'mid="'
			eTag = '"'
			pos1 = self.content.find(bTag,self.pos)+len(bTag)
			pos2 = self.content.find(eTag,pos1)
			self.weibomsg['mid'] = self.content[pos1:pos2]
			#print 'mid:'+self.weibomsg['mid']
			self.pos = pos2
			self.end = self.content.find(tag,self.pos) # self.end 定位当前处理微博的结束位置
			if self.end == -1:
				self.end = len(self.content)
		else:
			pass
	
	# 获取 message content(mc)
	def get_weibomc(self):
		tag = 'node-type="feed_list_content"'
		self.pos = self.content.find(tag, self.pos, self.end) + len(tag)
		bTag = '>'
		eTag = '<\/p>'
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		self.weibomsg['mc'] = self.content[pos1:pos2]
		self.weibomsg['mc'] = self.eraseTag(self.weibomsg['mc']).replace('\\','')
		self.weibomsg['mc'] = utility.clearSpace(self.weibomsg['mc']);
		self.pos = pos2
	
	# 解析转发消息的内容
	def get_retweet_info(self):
		tag = 'feed_list_forwardContent'
		pos =  self.content.find(tag, self.pos, self.end)
		temp = pos	#被删除的情况时，用到这个position
		if pos != -1:	#被删除的微薄，tag也能找到，下面注意限定范围
			self.pos = pos
			if( self.get_retweet_un() ):
				self.get_retweet_mc()
				self.get_weibopu()
				self.get_retweet_rc()
				self.get_retweet_cc()
				self.get_retweet_page()
				self.get_retweet_pt()
		else:
			pass	#转发信息都为空
	
	# 转发消息的用户名(run),转发微博未删除返回True,否则返回False
	def get_retweet_un(self):
		bTag = 'nick-name="'
		eTag = '"'
		pos1 = self.content.find(bTag, self.pos, self.end);
		if(pos1 != -1):
			pos1 = pos1 + len(bTag);
			pos2 = self.content.find(eTag, pos1, self.end)
			self.weibomsg['run'] = self.content[pos1:pos2]
			self.pos = pos2
			return True;
		else:
			return False;
	
	# 转发消息的内容(rmc)
	def get_retweet_mc(self):
		bTag = '<em>'
		eTag = '<\/em>'
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		self.weibomsg['rmc'] = self.content[pos1:pos2]
		self.pos = pos2
		self.weibomsg['rmc'] = self.eraseTag(self.weibomsg['rmc']).replace('\\','')
		self.weibomsg['rmc'] = utility.clearSpace(self.weibomsg['rmc']);
	
	# 微博中加载的图片的url(pu)，可能在转发里面，也有可能在原创微博里面
	def get_weibopu(self):
		tag = '<ul class="piclist">'
		pos = self.content.find(tag, self.pos, self.end)
		if pos != -1:
			bTag = 'src="'
			eTag = '"'
			pos1 = self.content.find(bTag,pos)+len(bTag)
			pos2 = self.content.find(eTag,pos1)
			self.weibomsg['pu'] = self.content[pos1:pos2].replace('\\','').replace('thumbnail','bmiddle')
			self.pos = pos2
		else:
			pass
	
	# 获取 retweet retweet count(rrc)
	def get_retweet_rc(self):
		bTag = '转发'
		eTag = '<\/a>'
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		if pos2-pos1 == 0:
			self.weibomsg['rrc'] = '0'
			self.pos = pos2
		else:
			slug = self.content[pos1:pos2]
			slug = utility.clearSpace(slug);
			self.weibomsg['rrc'] = slug[1:-1];
			self.pos = pos2
	
	# 获取 retweet comment count(rcc)
	def get_retweet_cc(self):
		bTag = '评论'
		eTag = '<\/a>'
		pos1 = self.content.find(bTag, self.pos, self.end)+len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		if pos2-pos1==0:
			self.weibomsg['rcc'] = '0'
			self.pos = pos2
		else:
			slug = self.content[pos1:pos2]
			slug = utility.clearSpace(slug);
			self.weibomsg['rcc'] = slug[1:-1];
			self.pos = pos2
	
	# 获取 retweet weibo page(rpage)
	def get_retweet_page(self):
		tag = '<a class="date"';
		self.pos = self.content.find(tag, self.pos, self.end) + len(tag)
		bTag = "href='";
		eTag = "'>";
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		temp = self.content[pos1:pos2].replace('\\','')
		self.weibomsg['rpage'] = temp
		self.pos = pos2 + 2

	# 获取 retweet publish time(rpt)
	def get_retweet_pt(self):
		eTag = '<\/a>'
		pos = self.content.find(eTag, self.pos, self.end);
		time = self.content[self.pos:pos];
		self.weibomsg['rpt'] = utility.time_format(time);
		self.pos = pos;
	
	# 获取 retweet count(rc)
	def get_weiborc(self):
		bTag = '转发'
		eTag = '<\/a>'
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag)
		pos2 = self.content.find(eTag, pos1, self.end)
		if pos2 - pos1 == 0:
			self.weibomsg['rc'] = '0'
			self.pos = pos2
		else:
			pos1 = pos1 + 1
			pos2 = pos2 - 1
			self.weibomsg['rc'] = self.content[pos1:pos2]
			self.pos = pos2
	
	# 获取 comment count(cc)
	def get_weibocc(self):
		bTag = '评论'
		eTag = '<\/a>'
		pos1 = self.content.find(bTag,self.pos,self.end)+len(bTag)
		pos2 = self.content.find(eTag,pos1,self.end)
		if pos2-pos1 == 0:
			self.weibomsg['cc'] = '0'
			self.pos = pos2
		else:
			pos1 = pos1 + 1
			pos2 = pos2 - 1
			self.weibomsg['cc'] = self.content[pos1:pos2]
			self.pos = pos2
	
	#weibo page and pt
	def get_weibo_page_pt(self):
		tag = 'node-type="feed_list_item_date"';
		self.pos = self.content.find(tag, self.pos, self.end) + len(tag) 
		slug = self.content[self.pos-70 : self.pos];
		bTag = 'title="';
		eTag = '"';
		pos1 = slug.find(bTag) + len(bTag);
		pos2 = slug.find(eTag, pos1);
		self.weibomsg['pt'] = slug[pos1:pos2];
		bTag = 'href="';
		eTag = '"';
		pos1 = self.content.find(bTag, self.pos, self.end) + len(bTag);
		pos2 = self.content.find(eTag, pos1);
		page = self.content[pos1:pos2];
		self.weibomsg['page'] = "http://www.weibo.com" + page.replace('\\','');
		self.pos = pos2;
	
	# 获取消息来源(srn)
	def get_weibo_srn(self):
		bTag = 'rel="nofollow">';
		pos1 = self.content.find(bTag, self.pos, self.end);
		if(pos1 == -1):
			return;
		pos1 = pos1 + len(bTag);
		eTag = '<\/a>'
		pos2 = self.content.find(eTag, pos1, self.end);
		self.weibomsg['srn'] = self.content[pos1:pos2]
		self.pos = pos2