import requests 
from lxml import etree
import os
import pysnooper
import get
import time

class book(object):
	"""docstring for book"""
	def __init__(self, url):
		self.url = url
		self.get_info()

	def get_info(self):
		header = {"User-Agent": "Mozilla/5.0"} 

		res = requests.get(self.url,headers=header)

		content = res.content
		html = etree.HTML(content)
		#获取页码
		page_num_str = html.xpath('//*[@id="chapterpager"]/a[8]/@href')
		self.chapter = html.xpath('//*[@class="active right-arrow"]')[0].text.strip().strip("...")
		try:	
			self.page_num = page_num_str[0][-3:].strip("/")
		except:
			self.page_num = 1
		#确定储存路径
		self.path = "./pic/"+self.chapter+"/"
		if os.path.exists(self.path) == False:
			os.mkdir(self.path)
		#获取全书的图片
		if self.page_num == 1:		#针对单页长页
			pic_list = get.get_img_norm(html,self.url) # 获得图片列表
			for pic,f_name in pic_list: 
				#写入图片
				write_pic(self.path,f_name,pic)
		else:						#针对翻页
			for num in range(1,int(self.page_num)+1):
				#获得图片以及文件名
				pic,f_name = get.get_img(html,num)
				#写入图片
				write_pic(self.path,f_name,pic)


	def __str__(self):
		return ("成功找到{} 共{}页".format(self.chapter,self.page_num))
def write_pic(path,f_name,pic):
	'''写入图片'''
	pic_path = path+f_name
	with open(pic_path,"wb") as f:
		f.write(pic)
		print("成功下载{}".format(pic_path))




if __name__ == '__main__':			
	#生成网址列表
	url_list = get.generate_url_list()
	#在网址列表遍历各个网址
	for url in url_list:
		comic  = book(url)	#建立一个book对象 
		print(comic)
		print("正在准备下次下载......")
		time.sleep(2)