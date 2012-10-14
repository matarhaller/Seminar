README for HW5

running answer_hw() will make a classifier and test it with three images. Everything was running really slow, so I wasn't able to test the classifier with large training and validation sets.

There is a problem with the way I'm making my training data sets, such that I can't make it with more than 2 samples per category (the outputted data structure is weird). That's the big bug that's screwing everything up.

You should be able to run run_final_classifier, but you need to give it both the path to the training data, and the path to the validation data.

It's been predicting many airplanes... I think that's because I can't give it enough training samples (because of the bug in how I make my training data).