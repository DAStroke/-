import requests 
from lxml import etree
import os
#import pysnooper
import time

header = {"User-Agent": "Mozilla/5.0","Referer": "http://www.1kkk.com"}	

#@pysnooper.snoop()
def extract_var(text,name,termin):
	'''提取文本中的变量'''
	start = text.find(name)+len(name)
	end = text[start:].find(termin)
	return text[start:][:end].strip('"')
def search_key(text):
	'''在文本中搜索key'''
	key_in_list = text.split("|")
	key_in_list = key_in_list[3:]
	key_in_list.sort(key=lambda x:len(x))
	key = key_in_list[-1]
	return key
def generate_url_list():
	'''生成网址列表'''
	url = "http://www.1kkk.com/manhua14421/"
	res = requests.get(url)
	html = etree.HTML(res.content)
	url_list = html.xpath('//*[@id="detail-list-select-1"]/li/a/@href')
	red_list = html.xpath('//*[@id="detail-list-select-1"]/ul/li/a/@href')
	url_list.extend(red_list)

	#print(url_list)	#for test
	return url_list
#@pysnooper.snoop()
def get_code_list(text):
	'''找出密码本'''
	code_book = extract_var(text[-220:],",'","'.split('|'),0,{}))").split("|")
	return code_book

#@pysnooper.snoop()
def get_head(text):
	'''提取出编码的head'''
	head_args = extract_var(text,"//",".").split("-")
	code_book = get_code_list(text)
	head = ""
	for i in head_args:
		try:	#判断是否为字母编码
			i = int(i)
		except:
			i = ord(i)-87
		head+=code_book[i]+"-"
	return head[:-1]	
#@pysnooper.snoop()
def get_page(text):
	page_arg = extract_var(text,'=["/',".")
	code_book = get_code_list(text)
	if type(page_arg) == str:	#判断是否为字母编码
		page_arg = ord(page_arg)-87
	page=code_book[page_arg]
	return page 
def get_img(html,num):
	'''获得图片'''
	#获得重要变量
	var_js = html.xpath('/html/head/*[@type="text/javascript"]')[-1].text.strip("\n")
	DM5_CURL = extract_var(var_js,"DM5_CURL = ",";")
	DM5_MID = extract_var(var_js,"DM5_MID=",";")
	DM5_CID = extract_var(var_js,"DM5_CID=",";")
	DM5_VIEWSIGN = extract_var(var_js,"DM5_VIEWSIGN=",";")
	DM5_VIEWSIGN_DT = extract_var(var_js,"DM5_VIEWSIGN_DT=",";").replace(":","%3A").replace(" ","+")
	#获得key
	key_url = "http://www.1kkk.com"+DM5_CURL+"chapterfun.ashx?cid="+DM5_CID+"&page="+str(num)+"&key=&language=1&gtk=6&_cid="+DM5_CID+"&_mid="+DM5_MID+"&_dt="+DM5_VIEWSIGN_DT+"&_sign="+DM5_VIEWSIGN
	key_res = requests.get(key_url,headers=header)
	key_text = key_res.text
	key = extract_var(key_text,"|dm5imagefun|","|")
	if len(key)<8:
		key = search_key(key_text)
	#获得页编码
	num_code = str(num)+"_"
	if "|"+num_code in key_text:
		page = str(num)+"_"+extract_var(key_text,str(num)+"_","|")
	else:
		page = get_page(key_text)
	#获得图片
	is_jpg = "|jpg|" in key_text
	#图片拓展名
	pic_type = jpg_or_png(is_jpg)
	#获得url的头
	url_head = get_head(key_text)
	#整合url
	img_url = "http://"+url_head+".cdndm5.com/15/"+DM5_MID+"/"+DM5_CID+"/"+page+pic_type+"?cid="+DM5_CID+"&key="+key+"&uk="
	#尝试访问图片url
	while True:
		try:	
			img_res = requests.get(img_url,headers=header)
			break
		except:
			print("访问出现问题,准备重试")
			time.sleep(2)

	if img_res.status_code != 200:
		print("图片有误！")
	pic = img_res.content
	#生成文件名
	f_name = generate_f_name(page,pic_type)
	return pic,f_name			#返回图片和文件名
def jpg_or_png(is_jpg):
	if is_jpg:
		return ".jpg"
	else:
		return ".png"

def generate_f_name(page,exten):
	'''整合图片的文件名'''
	termin = page.find("_")
	page = page[:termin]
	if len(page) == 1:
		page = "0"+page
	f_name = page+exten
	return f_name
def get_img_norm(html,url):
	'''长页网站的获取'''
	#获得图片url列表
	imgs = html.xpath('//*[@id="barChapter"]/img/@data-src')
	pic_list = []
	header = {"User-Agent": "Mozilla/5.0","Referer": url}
	#处理获得picture
	for img in imgs:
		#print(img)
		loc = img.find("_")-2 #减去页码
		end = img.find("?")
		f_list = img[loc:end].strip("/").split(".") #文件名和拓展名的列表
		f_name = generate_f_name(f_list[0],"."+f_list[1])
		pic_res = requests.get(img,headers=header)
		if pic_res.status_code != 200:
			print("图片有误！")
		pic = pic_res.content
		pic_list.append((pic,f_name))
	return pic_list

#@pysnooper.snoop()
def main():
	
	url_list = generate_url_list()

	url = url_list[0]
	#print(url)			#fortest
	for num in range(1,37):
		url_load = url+"/#ipg"+str(num)
		res = requests.get(url_load,headers=header)
		content = res.content
		html = etree.HTML(content)
		pic,f_name = get_img(html,num)
		
		path = "./pic/"+"第1章"+"/"
		if os.path.exists(path) == False:
			os.mkdir(path)
		with open(path+f_name,"wb") as f:
			f.write(pic)
			print("成功下载{}{}".format("第1章",f_name))


if __name__ == '__main__':
	main()