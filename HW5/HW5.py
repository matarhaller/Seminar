import numpy as np
from skimage import io
io.use_plugin('matplotlib')
from sklearn import cross_validation 
from sklearn.ensemble import RandomForestClassifier

#calculate features
def get_colorvalue(img):
	reds = img[:,:,0]
	greens = img[:,:,1]
	blues = img[:,:,2]
	return reds.mean(), greens.mean(), blues.mean()

def get_size(img):
	return img.shape

#def get_crosscorr(img):
#def get_edges(img):

def make_features(img,label = 0):
	"""
	input an image and returns the feature array
	if labels = some label string, then return a list list where the first element is the label string and the last element is the feature array
	"""
	r, g ,b = get_colorvalue(img)
	x, y, z = get_size(img)
	features = np.array([r,g,b,x,y])
	if label:
		labellist = list()
		labellist.append(label)
		labellist.append(features)
		return labellist
	else:
		return features

#define training and validation data set
data = np.array([make_features(img0,label =0), make_features(img1,label = 0), make_features(img2,label=0)])
labels = np.array(['airplanes', 'bats', 'airplanes'])

#create classifier
def make_classifier(data,labels):
	clf = RandomForestClassifier(n_estimators = 10)
	clf = clf.fit(data,labels)
	return clf

def make_prediction(clf,img):
	features = make_features(img,label =0)
	return clf.predict(features)


for f, c in trainingdict: #iterate over dictionary with cat/filename pairs
	#load data
	filename = '/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/' + c + '/' + x
	img = io.imread(filename)

img0 = io.imread('/Users/matar/Documents/Courses/50_categories/airplanes/airplanes_0001.jpg')

img1 = io.imread('/Users/matar/Documents/Courses/50_categories/bat/bat_0002.jpg')

img2 = io.imread('/Users/matar/Documents/Courses/50_categories/airplanes/airplanes_0002.jpg')

img3 = io.imread('/Users/matar/Documents/Courses/50_categories/bat/bat_0001.jpg')
