def get_img_norm(html):
	imgs = html.xpath('//*[@id="barChapter"]/img/@data-src')
	return imgs