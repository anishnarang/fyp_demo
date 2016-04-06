import random,shutil,os,Image

def make_composite(img1,img2,img3,img4):
	pic1 = Image.open("../mirflickr/im"+str(img1)+".jpg")
	pic2 = Image.open("../mirflickr/im"+str(img2)+".jpg")
	pic3 = Image.open("../mirflickr/im"+str(img3)+".jpg")
	pic4 = Image.open("../mirflickr/im"+str(img4)+".jpg")

	pic1 = pic1.resize((180, 150), Image.ANTIALIAS)
	pic2 = pic2.resize((180, 150), Image.ANTIALIAS)
	pic3 = pic3.resize((180, 150), Image.ANTIALIAS)
	pic4 = pic4.resize((180, 150), Image.ANTIALIAS)

	w1, h1 = pic1.size
	w2, h2 = pic2.size
	w3, h3 = pic3.size
	w4, h4 = pic4.size

	w = max(w1+w2,w3+w4)
	h = max(h1+h3,h2+h3)
	op_image = Image.new('RGB', (w, h))

	op_image.paste(pic1, (0,0))
	op_image.paste(pic2, (w1,0))
	op_image.paste(pic3, (0,h3))
	op_image.paste(pic4, (w1,h3))
	op_image.save("composite_image.jpg")

def get_all_images():
	temp = open("tags.txt").read().split(",")
	tags = []
	for i in temp:
		tags.append(i.strip())
	
	images = dict()
	for i in tags:
		l = open("annotate/"+str(i)+".txt").read().split("\n")
		for image in l:
			name = "im"+str(image)
			if name in images.keys():
				images[name].append(i)
			else:
				images[name] = []
				images[name].append(i)
	for image in images.keys():
		if len(images[image]) > 1:
			print image
			print " ".join(images[image])

if __name__ == "__main__":
	# rand_tags = set()
	# tags = []
	# temp = open("tags.txt").read().split(",")
	# for i in temp:
	# 	tags.append(i.strip())

	# while(len(rand_tags)<4):
	# 	rand_tags.add(random.randint(0,len(tags)-1))

	# images = dict()

	# for i in rand_tags:
	# 	l = open("annotate/"+str(tags[i])+".txt").read().split("\n")
	# 	images[l[random.randint(0,len(l)-1)].strip("\r")] = tags[i]
	get_all_images()
	# make_composite(*images.keys())