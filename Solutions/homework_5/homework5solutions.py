'''
Part of PySci sklearn homework solutions.
This program opens a saved (and trained) classifier
and applies it on new image data, saved in a folder called
`verification_images`
(must be organized into same hierarchy as `50_categories` folder).

IMPORTANT:
before running this script, you must run
$ python feature_calc.py
$ python train_classifier.py

Original Author: Chris Klein
Modified by: Isaac Shivvers
'''

import pickle
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

# open saved (and trained) classifier
clf = pickle.load( open('trained_classifier.p','r') )


# check to see if we've calculated features for the 
#  testing set yet - if not, calculate and save them
try:
    Xte, Yte, class_map, feature_names, test_image_names = pickle.load( open('testing_set.p','r') )
    print 'opening saved test set features...'
except:
    print 'calculating test set features...'
    # need to pull class_map and feature_names from training set
    Xtr, Ytr, class_map, feature_names, ignore = pickle.load( open('training_set.p','r') )
    # now, calculate all of the features for the testing set
    from feature_calc import calculate_features
    Xte, Yte, ignore, ignore, test_image_names = calculate_features( 'validation_images', 'testing_set.p', class_map=class_map)


print 'predicting the classes of verification images...'
pred = clf.predict(Xte)
rfor_01_score = metrics.zero_one_score(Yte, pred) # zero-one score
print "Zero-One Score: " + str(rfor_01_score)

# create and save the confusion matrix
confmat = metrics.confusion_matrix(Yte, pred)
plt.close("all")
plt.imshow(confmat, interpolation="nearest", origin="upper")
plt.savefig("confusion_matrix.pdf")
plt.close("all")

# show the feature importances
print "Summary of feature importances"
for n in range(len(feature_names)):
    print "\t", round(clf.feature_importances_[n], 4), feature_names[n]

# reverse the class_map to get the names for each category
class_unmap = {}
for key in class_map.keys():
    class_unmap[ class_map[key] ] = key
predictions = [class_unmap[val] for val in pred]

# Write out the results file as requested.
results_file = file("results.txt", "w")
results_file.write("filename\t\tpredicted_class\n")
results_file.write("-----------------------------------------\n")
for n,name in enumerate(test_image_names):
    results_file.write(name.split("/")[-1] + "\t" + predictions[n] + "\n")
results_file.close()
