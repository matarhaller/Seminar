'''
Part of PySci sklearn homework solution.
This program trains a Random Forest classifier
on features saved in a pre-computed file
`training_set.p`

Original Author: Chris Klein, 2012
Modified by: Isaac Shivvers, 2012
'''

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import grid_search, metrics

from scipy import *
from pylab import *
import pickle


# open saved training set features and categories
Xtr, Ytr, class_map, feature_names, image_names = pickle.load( open('training_set.p','r') )

# build our classifier
clf = RandomForestClassifier(n_estimators=1000, n_jobs=-1, compute_importances=True)

# fit to the data
print 'fitting RandomForest to training set...'
clf.fit(Xtr, Ytr)

# calculate CV score
print 'calculating cross-validation score...'
scores = cross_val_score(clf, Xtr, Ytr)
print "Cross-validation score", scores.mean()

# save classifier for posterity (this may be a very large file)
pickle.dump( clf, open('trained_classifier.p','w') )

