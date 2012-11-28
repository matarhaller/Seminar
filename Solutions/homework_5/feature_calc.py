'''
Part of Homework solution to PySci sklearn problem set.
This program calculates a set of features for all images
in a folder.

This takes advantage of the multiprocessing module
to calculate features in parallel, since feature
calculation is an embarassingly parallel problem.
(See http://en.wikipedia.org/wiki/Embarrassingly_parallel.)

Original Author: Chris Klein, 2012
Modified: Isaac Shivvers, 2012
'''


from os import listdir, system
from multiprocessing import Pool, cpu_count
from time import time
from sys import argv
from pylab import *
from scipy import *
from scipy import ndimage
from skimage import img_as_float, color, filter, exposure, feature, morphology
import pickle

def split_seq(seq, size):
    '''
    Divides up a large list into multiple small lists, 
    attempting to keep them all the same size.
    '''
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
            int(round((i+1)*splitsize))])
    return newseq


def extract_features(image_path_list):
    '''
    Our feature extraction function. It takes in a list of image paths, 
    does some measurement on each image, then returns a list of the image paths
    paired with the results of the feature measurement.
    '''
    feature_list = []
    for image_path in image_path_list:
        image_array = imread(image_path)
        if len(image_array.shape) != 3:
            image_array = color.gray2rgb(image_array)

        # Create a sub-image of the center. Useful for color of subject.
        height, width = image_array.shape[0], image_array.shape[1]
        central_y, central_x = int(round(height/2.0)), int(round(width/2.0))
        central_image_array = image_array[central_y-height/10 : central_y+height/10, central_x-width/10 : central_x+width/10, :]

        # crop to square integer 16x16 size
        new_height, new_width = 16*(height/16), 16*(width/16)
        if new_height < new_width: new_width = new_height
        elif new_height > new_width: new_height = new_width
        cropped_image_array = image_array[central_y-new_height/2 : central_y+new_height/2, central_x-new_width/2 : central_x+new_width/2, :]
        #Equalize the image
        image_array_gray_equalized = exposure.equalize(color.rgb2gray(cropped_image_array))
        # Now zoom it to 128x128 for easier shape processing
        small_square_gray_image = ndimage.interpolation.zoom(image_array_gray_equalized, 128.0/new_height)

        # Create sobel filtered image
        sobel_image = ndimage.filters.sobel(image_array)
        # (1) Number of pixels in the image (super simple)
        n_pixels = image_array.size
        # (2) Median red value
        med_red_val = median(central_image_array[:,:,0])
        # (3) Median green value
        med_green_val = median(central_image_array[:,:,1])
        # (4) Median blue value
        med_blue_val = median(central_image_array[:,:,2])
        # (5) Standard Deviation of red value
        std_red_val = central_image_array[:,:,0].std()
        # (6) Standard Deviation of green value
        std_green_val = central_image_array[:,:,1].std()
        # (7) Standard Deviation of blue value
        std_blue_val = central_image_array[:,:,2].std()
        # (8) Image aspect ratio (width/height)
        aspect_ratio = float(width)/height
        # (9) Histogram Otsu thershold
        otsu_thresh = filter.threshold_otsu(image_array)
        # (10, 11, 12) Center of Mass
        center_of_mass_x, center_of_mass_y, center_of_mass_value = ndimage.measurements.center_of_mass(image_array)
        # (13) Ratio of sum of bottom half vs top half of pixels
        vertical_ratio = small_square_gray_image[:64,:].sum()/small_square_gray_image[64:,:].sum()
        # (14) Ratio of sum of left half vs right half of pixels
        horizontal_ratio = small_square_gray_image[:,:64].sum()/small_square_gray_image[:,64:].sum()
        # (15, 16, 17) Location of maximum
        max_x, max_y, max_band = ndimage.measurements.maximum_position(image_array)
        # (18, 19, 20) Location of minimum
        min_x, min_y, min_band = ndimage.measurements.minimum_position(image_array)
        # (21) Median sobel red value
        med_sobel_red_val = median(sobel_image[:,:,0])
        # (22) Median sobel green value
        med_sobel_green_val = median(sobel_image[:,:,1])
        # (23) Median sobel blue value
        med_sobel_blue_val = median(sobel_image[:,:,2])
        # (24) Standard Deviation of sobel red value
        std_sobel_red_val = sobel_image[:,:,0].std()
        # (25) Standard Deviation of sobel green value
        std_sobel_green_val = sobel_image[:,:,1].std()
        # (26) Standard Deviation of sobel blue value
        std_sobel_blue_val = sobel_image[:,:,2].std()
        # (27) Number of Harris points
        n_harris_points = feature.harris(small_square_gray_image, min_distance=6).size
        # (28) Mean of Histogram of Gradients (HOG)
        fd = feature.hog(image_array_gray_equalized, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=False)
        mean_hog = fd.mean()
        # (29) Standard Deviation of Histogram of Gradients (HOG)
        std_hog = fd.std()
        # (30) Ratio of white pixels in skeletonized image
        edge_image = filter.canny(image_array_gray_equalized, sigma=1)
        skeleton_image = morphology.skeletonize(edge_image)
        skeleton_ratio = float(skeleton_image.sum())/skeleton_image.size

        feature_list.append([image_path, 
            n_pixels,
            med_red_val,
            med_green_val,
            med_blue_val,
            std_red_val,
            std_green_val,
            std_blue_val,
            aspect_ratio,
            otsu_thresh,
            center_of_mass_x,
            center_of_mass_y,
            center_of_mass_value,
            vertical_ratio,
            horizontal_ratio,
            max_x, 
            max_y, 
            max_band,
            min_x,
            min_y,
            min_band,
            med_sobel_red_val,
            med_sobel_green_val,
            med_sobel_blue_val,
            std_sobel_red_val,
            std_sobel_green_val,
            std_sobel_blue_val,
            n_harris_points,
            mean_hog,
            std_hog,
            skeleton_ratio])            
    return feature_list

# keep track of feature names as well
feature_names = ["n_pixels",
            "med_red_val",
            "med_green_val",
            "med_blue_val",
            "std_red_val",
            "std_green_val",
            "std_blue_val",
            "aspect_ratio",
            "otsu_thresh",
            "center_of_mass_x",
            "center_of_mass_y",
            "center_of_mass_value",
            "vertical_ratio",
            "horizontal_ratio",
            "max_x", 
            "max_y", 
            "max_band",
            "min_x",
            "min_y",
            "min_band",
            "med_sobel_red_val",
            "med_sobel_green_val",
            "med_sobel_blue_val",
            "std_sobel_red_val",
            "std_sobel_green_val",
            "std_sobel_blue_val",
            "n_harris_points",
            "mean_hog",
            "std_hog",
            "skeleton_ratio"]

def find_all_images(base_directory):
    '''
    finds all the images in base_directory, returning
    a list of paths to the images as well as the
    category of each image, if it exists.
    '''
    # Find all of the images
    image_paths = []
    categories = listdir(base_directory)
    vetted_categories = []
    for n in range(len(categories)):
        if categories[n][0] != ".": vetted_categories.append(categories[n])
    categories = vetted_categories
    for category in categories:
        image_names = listdir(base_directory + '/' + category)
        for name in image_names:
            if 'jpg' not in name: continue
            image_paths.append(base_directory + '/' + category + "/" + name)
    return image_paths, categories



### Main function starts here ###################################################
def calculate_features(directory, save_file_name, class_map=None):
    '''
    Extract features for all images in directory
    (formatted with same hierarchy as 50_categories directory)
    and save to a pickle file.
    
    If given the class_map argument (a dictionary), will map image categories
    onto integers as defined by class_map.
    '''
    
    paths, categories = find_all_images(directory)
    
    if class_map == None:
        # The classifier requires each class (or category) to be identified
        #  by an integer, so make dictionaries to map each class onto an integer and back
        class_map = {}
        for i,cat in enumerate(categories):
            class_map[cat] = i

    # Run the feature extraction function using multiprocessing.Pool so 
    #  so that we can parallelize the process and run it much faster.
    numprocessors = cpu_count() # To see results of parallelizing, set numprocessors
                                # to less than cpu_count().
    # We have to cut up the image_paths list into the number of processes we want to run. 
    split_paths = split_seq(paths, numprocessors)

    # This block is where the parallel code runs. We time it so we can get a 
    #  feel for the speed up.
    start_time = time()
    print 'starting extraction with', numprocessors,'processors'
    p = Pool(numprocessors)
    result = p.map_async(extract_features, split_paths)
    poolresult = result.get()
    end_time = time()
    # All done, print timing results.
    print ("Finished extracting features. Total time: " + 
        str(round(end_time-start_time, 3)) + " s, or " + 
        str( round( (end_time-start_time)/len(paths), 5 ) ) + " s/image.")
    # This takes ~300 seconds on my MacBook air for the training set of images
    
    # create a final list of the feature extraction results for all images.
    image_names = []
    features = []
    image_categories = []
    for single_proc_result in poolresult:
        for single_image_result in single_proc_result:
            image_names.append(single_image_result[0])
            image_categories.append(single_image_result[0].split("/")[1])
            features.append(single_image_result[1:])

    # X are the features (data)
    X = array(features)
    # Y are the categories (target)
    int_val_categories = [class_map[val] for val in image_categories]
    Y = array(int_val_categories)

    # save everything to file, so we only need to do this once
    pickle.dump( [X, Y, class_map, feature_names, image_names], open(save_file_name,'w'))
    
    return [X, Y, class_map, feature_names, image_names]


#######################################################
## run from command line to process training set data
if __name__ == '__main__':
    _ = calculate_features('50_categories','training_set.p')