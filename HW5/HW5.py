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

def make_features(img):
	r, g ,b = get_colorvalue(img)
	x, y, z = get_size(img)
	features = np.array([r,g,b,x,y])
	return features


for f, c in trainingdict: #iterate over dictionary with cat/filename pairs
	#load data
	filename = '/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/' + c + '/' + x
	img = io.imread(filename)
	


img0 = io.imread('/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/airplanes/airplanes_0001.jpg')

img1 = io.imread('/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/bat/bat_0002.jpg')

img2 = io.imread('/Users/matar/Documents/Courses/PythonClass/HW5/50_categories/airplanes/airplanes_0002.jpg')

data = np.array([make_features(img0), make_features(img1), make_features(img2)])

#run random trees