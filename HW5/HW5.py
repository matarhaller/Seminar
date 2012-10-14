import numpy as np
#from skimage import io
from scipy import misc
#io.use_plugin('matplotlib')
from sklearn import cross_validation 
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA

#calculate features
def get_colorvalue(img):
	reds = img[:,:,0]
	greens = img[:,:,1]
	blues = img[:,:,2]
	return reds.mean(), greens.mean(), blues.mean()

def get_size(img):
	return img.shape

def get_PCA(img):
	"""
	return mean of first 3 principal components
	"""
	pca = PCA(n_components = 3, whiten = True).fit(img.mean(axis=2))
	return pca.components_.mean(axis=1)

#def get_crosscorr(img):
#def get_edges(img):
	#edges = skimage.filter.sobel(img)
	#return edges

def make_features(img,label = 0):
	"""
	input an image and returns the feature array
	if labels = some label string, then return a list list where the first element is the label string and the last element is the feature array
	"""
	r, g ,b = get_colorvalue(img)
	x, y, z = get_size(img)
	p = get_PCA(img)
	features = np.array([r,g,b,x,y,p[0],p[1],p[2]])
	if label:
		labellist = list()
		labellist.append(label)
		labellist.append(features)
		return labellist
	else:
		return features

#create classifier
def make_classifier(data,labels):
	clf = RandomForestClassifier(n_estimators = 10, max_depth = 3)
	clf = clf.fit(data,labels)
	return clf

def make_prediction(clf,img):
	features = make_features(img,label =0)
	return clf.predict(features)


#for f, c in trainingdict: #iterate over dictionary with cat/filename pairs
	#load data
#	filename = '/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/' +#	img = io.imread(filename)


img0 = misc.imread('/Users/matar/Documents/Courses/50_categories/airplanes/airplanes_0001.jpg')

img1 = misc.imread('/Users/matar/Documents/Courses/50_categories/bat/bat_0002.jpg')

img2 = misc.imread('/Users/matar/Documents/Courses/50_categories/airplanes/airplanes_0002.jpg')

img3 = misc.imread('/Users/matar/Documents/Courses/50_categories/bat/bat_0001.jpg')

#define training and validation data set
data = np.array([make_features(img0,label =0), make_features(img1,label = 0), make_features(img2,label=0)])
labels = np.array(['airplanes', 'bats', 'airplanes'])

def answer_hw():
	print "answering hw"
	clf = make_classifier(data,labels)
	print make_prediction(clf,img3)

