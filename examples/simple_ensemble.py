"""
This file demos a simple ensembling of sklearn
models on the iris dataset. This is meant to 
function more as a demo/plumbing check than a 
state of the art result
"""

from sklearn.svm import SVC as svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

from numpy import ndarray
import numpy as np
import seaborn as sns

from ds_ensemble.DSEnsemble import DSEnsemble as DSE
from ds_ensemble.Model import Model

# create some normalization functions to help
# demo data transforms for ensembling
def normalize_iris_data(unnorm_data: ndarray):
    # for each feature in the dataset, make the values 
    # 0 mean 1 std
    # we copy to not affect the passed in data
    norm_data = unnorm_data.copy()

    for feat_num in range(unnorm_data.shape[1]):
        # get the mean and var
        mean = np.mean(unnorm_data[:][feat_num])
        std = np.std(unnorm_data[:][feat_num])

        # apply to the data in place
        norm_data[:][feat_num] = (unnorm_data[:][feat_num] - mean) / float(std)

    # return the normalize array
    return norm_data

if __name__=='__main__':
    # load in the iris dataset
    (x,y) = load_iris(return_X_y=True)

    # split our data into holdout/train
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

    # holdout an extra bit of data from train to use as the evaluation set
    # for DSE
    x_train, x_eval, y_train, y_eval = train_test_split(x_train, y_train, test_size=0.2)

    # create our two classifiers
    clf_svm = svm()
    clf_knn = KNeighborsClassifier(n_neighbors=3)

    # just for demo purposes we will only normalize the knn model data
    # to highlight that we could have different normalization approaches 
    # on a per model basis
    x_train_norm = normalize_iris_data(x_train)

    # fit our models now
    clf_svm.fit(x_train, y_train)
    clf_knn.fit(x_train_norm, y_train)

    # place them in the model wrapper
    svm_wrap = Model(trained_model = clf_svm,
                     model_type = 'sklearn',
                     output_classes = ['0', '1', '2'],
                     preprocess_function = None
                    )
    
    knn_wrap = Model(trained_model = clf_knn,
                     model_type = 'sklearn',
                     output_classes = ['0', '1', '2'],
                     preprocess_function = normalize_iris_data
                    )

    # now setup the beliefs for each model based on our eval set
    svm_wrap.setup_beliefs([x_eval, y_eval])
    knn_wrap.setup_beliefs([x_eval, y_eval])

    # now we instantiate our ds ensembling
    dse = DSE(models=[svm_wrap, knn_wrap])

    # finally we can predict on our test set using belief as
    # the predictor method
    results = dse.predict(x_test, decision_metric='bel')
    for pred, true in zip(results, y_test):
        print("Pred: ", pred, ", True: ", true)


    # see the accuracy of the results
    cf_matrix = confusion_matrix(results, y_test)
    print(cf_matrix)