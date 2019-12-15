from PIL import Image, ImageDraw, ImageFont
import click

def pixels2data(pixels):
	pixels_out = []
	for row in pixels:
		for tup in row:
			pixels_out.append(tup)
	return pixels_out

def sliding(image, right=0, down=0):
	image = image.copy()
	width, height = image.size
	pixels   = list(image.getdata())
	pixels   = [ pixels[i * width:(i + 1) * width] for i in xrange(height) ]
	new_pixels = [ [ (255,255,255) for j in xrange(width) ] for i in xrange(height) ]
	# check image width and height
	if (right < width) or (down < height):
		for y in range(down,height):
			for x in range(down,width):
				new_pixels[y][x] = pixels[y-down][x-down]
		image.putdata(pixels2data(new_pixels))
		return image
	else:
		return image

def text2img(text,height,width, font_size = 24):
	img = Image.new('RGB', (height, width), color = (255,255,255))
	d = ImageDraw.Draw(img)
	font = ImageFont.truetype('impact.ttf', font_size)
	d.text((0,0), text, fill = (0,0,0), font=font)
	return img

def zoomIn(image):
	img = image.copy()
	width, height = img.size
	pixels = list(img.getdata())
	new_pixels = []
	pixels_satu = []
	
	pixels   = [ pixels[i * width:(i + 1) * width] for i in range(height) ]
	for x in range(height):
		pixels_satu = []
		for y in range(width):
			for z in range(width):
				pixels_satu.append(pixels[x][y])
		for v in range(height):
			new_pixels.append(pixels_satu)

	width = pow(width,2)
	height = pow(height,2)
	new_img = Image.new('RGB', (height, width), color = (255,255,255))
	new_img.putdata(pixels2data(new_pixels))
	return new_img

def toZoomOut(image): 
	img = image.copy()
	width, height = img.size
	if (width%2==0) : return 2
	elif (width%3==0) : return 3
	elif (width%5==0) : return 5
	elif (width%7==0) : return 7

def zoomOut(image,scale):
	img = image.copy()
	width, height = img.size
	pixels = list(img.getdata())
	pixels = [ pixels[i * width:(i + 1) * width] for i in range(height) ]
	# for pixel in pixels:
	# 	print pixel
	new_pixels = []
	pixels_satu = []
	size = width/scale
	for v in range(0,height,height/size):
		# print "v = ",v
		for w in range(0,width,width/size):
			# print "w = ",w
			R,G,B,jum=0,0,0,0
			for y in range(v,v+height/size):
				for x in range(w,w+width/size):
					# print y,x
					xR,xG,xB = pixels[y][x]
					R = R+xR
					G = G+xG
					B = B+xB
					jum = jum+1
			pixels_satu.append((R/jum,G/jum,B/jum))

	# for pixel in pixels_satu:
	# 	print pixel
	for x in range(0,len(pixels_satu),size):
		a = pixels_satu[x:x+size]
		new_pixels.append(a)
	# print "==================="
	# for pixel in new_pixels:
	# 	print pixel
	
	width = size
	height = size
	new_img = Image.new('RGB', (height, width), color = (255,255,255))
	new_img.putdata(pixels2data(new_pixels))
	return new_img

def intToBin(rgb):
	r, g, b = rgb
	return ('{0:08b}'.format(r),'{0:08b}'.format(g),'{0:08b}'.format(b))

def binToInt(rgb):
	r, g, b = rgb
	return (int(r, 2), int(g, 2),int(b, 2))

def mergeRgb(rgb1,rgb2):
	r1, g1, b1 = rgb1
	r2, g2, b2 = rgb2
	rgb = (r1[:6] + r2[-2:],
           g1[:6] + g2[-2:],
           b1[:6] + b2[-2:])
	return rgb

def merge_image(image1,image2):
	image1 = image1.copy()
	image2 = image2.copy()

	if image2.size[0] > image1.size[0] or image2.size[1] > image1.size[1]:
		return 'Gambar 2 harus lebih kecil dibanding gambar 1'

	pixel_image1 = image1.load()
	pixel_image2 = image2.load()

	new_image = Image.new(image1.mode, image1.size)
	pixels_new = new_image.load()

	for i in range(image1.size[0]):
		for j in range(image1.size[1]):
			# print intToBin(pixel_image1[i,j])
			rgb1 = intToBin(pixel_image1[i,j])
			rgb2 = intToBin((0,0,0))

			if i < image2.size[0] and j < image2.size[1]:
				rgb2 = intToBin(pixel_image2[i, j])

			rgb = mergeRgb(rgb1,rgb2)

			pixels_new[i,j] = binToInt(rgb)
	return new_image

def directly_merge(image, text):
	image = image.copy()
	width, height = image.size
	text_image = text2img(text, int(width*0.8), int(height*0.8), int(height * 0.4))
	return merge_image(image,text_image)

def getPlane(img, channel, index = 0):
	if channel in img.mode:
		new_image = Image.new('1', img.size)
		new_image_data = new_image.load()

		img_data = img.load()

		channel_index = img.mode.index(channel)

		for x in range(img.size[0]):
			for y in range(img.size[1]):
				color = img_data[x,y]
				channel = color[channel_index]
				plane = bin(channel)[2:].zfill(8)
				try:
					new_image_data[x,y] = 255*int(plane[abs(index-7)])
				except IndexError:
					pass
		return new_image

@click.command()
@click.option('--message', help='Message text')
@click.option('--height', default=50, help='height the message')
@click.option('--width', default=50, help='width message')
@click.option('--output', default='', help='Ouput file')
@click.option('--zoom_in', help='Zoom In the message')
@click.option('--zoom_out', help='Zoom Out the message')
@click.option('--sliding_right', help='Zoom the message')
@click.option('--sliding_bottom', help='Zoom the message')
@click.option('--source', help='Zoom the message')
@click.option('--merge', help='Merge two image')
@click.option('-e', help='Extract Image')
def cli(message, height, width, output, zoom_in, sliding_right, sliding_bottom, source, zoom_out, merge, e):
	image = Image.new('RGB',(height,width),color=(255,255,255))
	if source == None and message != None:
		image = text2img(message, height, width)
	if source != None:
		image = Image.open(source)

	# zoom in
	if zoom_in == 'true':
		image = zoomIn(image)
		output = output if output != '' else 'zoom_in'
		image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))

    # Zoom Out
	if zoom_out == 'true':
		image = zoomOut(image,toZoomOut(image))
		output = output if output != '' else 'zoom_out'
		image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))

	# sliding image
	if sliding_right != None and sliding_bottom != None:
		image = sliding(image,int(sliding_right),int(sliding_bottom))
		output = output if output != '' else 'sliding'
		image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))
	
	if e != None:
		image = Image.open(e)
		for channel in image.mode:
			for plane in range(8):
				x = getPlane(image,channel,plane)
				file_name = e.split('.')[0]
				click.echo('created {}_{}{}.jpg'.format(file_name,channel,plane))
				x.save('{}_{}{}.jpg'.format(file_name,channel,plane))

	# merge image
	if merge != None and source != None and e == None:
		img1 = Image.open(source)
		img2 = Image.open(merge)
		new_image = merge_image(img1,img2)
		output = output if output != '' else 'merged'
		new_image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))

	#directly merge with message
	if merge != None and message != None:
		image = Image.open(merge)
		new_image = directly_merge(image, message)
		output = output if output != '' else 'merged'
		new_image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))

	# message pic
	if zoom_in != 'true' and zoom_out != 'true' and sliding_right == None and sliding_bottom == None and merge == None and message != None:
		output = output if output != '' else 'output'
		image.save('{}.jpg'.format(output))
		click.echo('created {}.jpg'.format(output))


if __name__ == '__main__':
    cli()