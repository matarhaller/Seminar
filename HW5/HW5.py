import numpy as np
from skimage import io
io.use_plugin('matplotlib')
from scipy import misc
from sklearn import cross_validation 
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from scipy import signal
from skimage import filter
from matplotlib import mlab
from scipy import ndimage
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage import img_as_float
from skimage import transform
import glob
from skimage.segmentation import random_walker

#methods for features
def get_colorvalue(img):
	if np.size(img.shape) == 3: #color image
		reds = img[:,:,0]
		greens = img[:,:,1]
		blues = img[:,:,2]
	else:
		reds = img[:,0]
		greens = img[:,1]
		blues = greens
	colors = np.array([[reds.mean(), greens.mean(), blues.mean()]])
	return img_as_float(colors)

def get_size(img):
	return np.array(img.shape)

def get_localmax(img):
	im = img_as_float(img)
	img_max = ndimage.maximum_filter(im, size=20,mode = 'constant')
	coordinates = peak_local_max(im,min_distance = 20)
	return coordinates

def get_edges(img):
	edges = skimage.filter.canny(img.mean(axis =2),sigma = 3)
	return edges

def get_segments(img):
	markers = np.zeros(data.shape, dtype=np.uint)
	markers[img < -0.3] = 1
	markers[img > 1.3] = 2
	labels = random_walker(img, markers,beta = 10, mode = 'bf')

def make_features(img,label = 0): 
	"""
	input an image and returns the feature array
	if labels = some label string, then return a list list where the first element is the label string and the last element is the feature array
	"""
	colors = get_colorvalue(img)
	sz = get_size(img)
	coord = get_localmax(img)
	features = np.append(colors,coord[0:50,0]) 
	features = np.append(features,coord[0:50,1])
	features = np.append(features,sz)
	if label:
		labellist = list()
		labellist.append(label)
		labellist.append(features)
		return labellist
	else:
		return features

#create classifier
def make_data(path,numtraining):
	categories = [x.split('/')[-1] for x in glob.glob(path+'*')]
	labels = list()
	for idx, c in enumerate(categories):
		files = glob.glob(path  + c + '/*jpg')
		labelsf = list()
		for f in range(numtraining):
			img = io.imread(files[f])
			labelsf.append(c)
			if f == 0 & idx == 0:
				data = make_features(img)
			else:
				data = np.array([data, make_features(img)])
		labels.extend(labelsf)
	return data, labels

def make_classifier(data,labels):
	clf = RandomForestClassifier()
	clf = clf.fit(data,labels)
	return clf

def make_prediction(clf,img):
	features = make_features(img)
	return clf.predict(features)

def run_final_classifier(trainingpath,validationpath):
	print "making data..."
	data, labels = make_data(trainingpath,10)
	print "making classifier..."
	clf = make_classifier(data,labels)

	filelist = glob.glob(validationpath+'validation*.jpg')
	predictions = dict()
	for f in filelist:
		img = io.imread(f)
		predictions[f] = make_prediction(clf,f)
	print 'filename \t\t predicted_class'
	print "-"*40
	for k in predictions.keys():
		print k + "\t\t" + predictions[k]

def answer_hw():
	print "answering hw"
	path = '../../50_categories/'
	img0 = io.imread(path + 'airplanes/airplanes_0001.jpg')

	img1 = io.imread(path + 'bat/bat_0002.jpg')

	img2 = io.imread(path + 'airplanes/airplanes_0002.jpg')

	img3 = io.imread(path + 'bat/bat_0001.jpg')
	
	#make classifier
	print "making training data..."
	data, labels = make_data(path,5)

	print "making classifier..."
	clf = make_classifier(data,labels)
	print "actual: bat"
	print "predicted: " 
	print make_prediction(clf,img3)

