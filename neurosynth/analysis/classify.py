
import numpy as np

def classify_by_features(dataset, features, studies=None, method='SVM', scikit_classifier=None):
    pass

def classify_regions(dataset, masks, remove_overlap=True, threshold=0.001, what_to_return=None, studies=None, method='SVM', classifier=None, regularization="Alejandro's expert judgment"):
    # for m in masks:
    #     - load the image from file
    #     - select studies that activate within masks
    # if remove_overlap:
    #     remove overlap
    # labels--assign class labels
    # return classify(input=dataset, features='features', classes=labels, None)
    pass

def decode_by_features():
    pass

def decode_by_masks():
    pass



class Decoder:

    def __init__(self, method='pearson', dataset=None, features=None, classifier='SVM', **kwargs):
        # self.classifiers = train_classifiers(None)
        pass


    def train_classifiers(self, features=None):
        ''' Train a set of classifiers '''
        # for f in features:
        #     clf = Classifier(None)
        #     self.classifiers.append(clf)
        pass


    def decode(self, X):
        # loops over classifiers and images and writes out a value
        pass


class Classifier:

 

    def __init__(self, method='SVM', classifier=None, class_weight=None):
        """ Initialize a new classifier instance """
        if classifier:
            self.sk_classifier = classifier
        else:
            if method == 'SVM':
                from sklearn import svm
                self.sk_classifier = svm.SVC(class_weight=class_weight)
            else:
                # Error handling?
                self.sk_classifier = None


    def fit(self, X, y):
        """ Fits X to outcomes y, using sk_classifier """
        # Incorporate error checking such as :
        # if isinstance(self.classifier, ScikitClassifier):
        #     do one thingNone
        # otherwiseNone. 

        self.X = X
        self.y = y
        self.sk_classifier.fit(X, y)

    def cross_val_fit(self, X, y):
        pass

    def fit_dataset(self, dataset, y, features=None, feature_type='features'):
        """ Given a dataset, fits either features or voxels to y """

        # Get data from dataset
        if feature_type=='features':
            X = np.rot90(dataset.feature_table.data.toarray())
        elif feature_type=='voxels':
            X = np.rot90(dataset.image_table.data.toarray())

        self.sk_classifier.fit(X,y)

    def regularize(self, X, method='None'):
        # Nonewhat to give scikitNone or do it yourselfNone
        return X

    def classify(inputs=None, features=None, classes=None, what_to_return=None, cross_val=None):
        # inputs: dataset, list of images
        # features: voxels, features
        # classes: vector of class assignments
        pass



class PearsonClassifier:

    def __init__(self):
        pass

    def fit(self):
        # just calculate the max and call that the class
        pass

    def predict(self):
        pass
