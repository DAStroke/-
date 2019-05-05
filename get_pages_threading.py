import requests 
from lxml import etree
import threading

class book(threading.Thread):
	"""docstring for book"""
	def __init__(self, arg):
		super(book, self).__init__()
		self.url = url
		self.get_info()

	def get_info(self):
		header = {"User-Agent": "Mozilla/5.0"} 

		try:
			res = requests.get(self.url,headers=header)
			if res.status_code == 200:
				content = res.content
				html = etree.HTML(content)
				#获取页码
				page_num_str = html.xpath('//*[@id="chapterpager"]/a[8]/@href')
				self.chapter = html.xpath('//*[@class="active right-arrow"]')[0].text.strip()
				try:	
					self.page_num = page_num_str[0][-3:].strip("/")
				except:
					self.page_num = 1
				#print(page_num)	#fortest
				#print(chapter)		#fortest
			else:
				print("出现异常"+str(res.status_code))
		except:
			print("网络异常或不知名错误！")
	def __str__(self):
		return ("成功找到{}共{}页".format(self.chapter,self.page_num))
if __name__ == '__main__':			
	#生成网址列表
	url_list = []

	with open("ct.csv","r") as f:
		for url in f.readlines():
			url_list.append(url.strip("\n"))

	#print(url_list)	#for test

	for url in url_list:
		comic  = book(url) 
		print(comic)