#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Classification and decoding related tools """

import numpy as np
from functools import reduce


def classify_by_features(dataset, features, studies=None, method='SVM',
                         scikit_classifier=None):
    pass

def regularize(X, method='scale'):
    if method == 'scale':
        from sklearn import preprocessing
        return preprocessing.scale(X, with_mean=False)
    else:
        raise Exception('Unrecognized regularization method')

def get_studies_by_regions(dataset, masks, threshold=0.08,
                           remove_overlap=True, studies=None,
                           features=None, regularization="scale"):
    """ Set up data for a classification task given a set of masks
    
        Given a set of masks, this function retrieves studies associated with each 
        mask at the specified threshold, optionally removes overlap and filters by studies 
        and features, and returns studies by feature matrix (X) and class labels (y)

        Args:
            dataset: a Neurosynth dataset
            maks: a list of paths to Nifti masks
            threshold: percentage of voxels active within the mask for study to be included
            remove_overlap: A boolean indicating if studies studies that appear in more than 
                one mask should be excluded
            studies: An optional list of study names used to constrain the set used in
                classification. If None, will use all features in the dataset.
            features: An optional list of feature names used to constrain the set used in
                classification. If None, will use all features in the dataset.
            regularize: Optional boolean indicating if X should be regularized

        Returns:
            A tuple (X, y) of np arrays. 
            X is a feature by studies matrix and y is a vector of class labels
    """

    import nibabel as nib
    import os

    # Load masks using NiBabel

    try:
        loaded_masks = [nib.load(os.path.relpath(m)) for m in masks]
    except OSError:
        print 'Error loading masks. Check the path'

    # Get a list of studies that activate for each mask file--i.e.,  a list of
    # lists

    grouped_ids = [dataset.get_ids_by_mask(m, threshold=threshold)
                   for m in loaded_masks]

    # Flattened ids

    flat_ids = reduce(lambda a, b: a + b, grouped_ids)

    # Remove duplicates

    if remove_overlap:
        import collections
        flat_ids = [id for (id, count) in
                    collections.Counter(flat_ids).items() if count == 1]
        grouped_ids = [[x for x in m if x in flat_ids] for m in
                       grouped_ids]  # Remove

    # Create class label(y)

    y = [[idx] * len(ids) for (idx, ids) in enumerate(grouped_ids)]
    y = reduce(lambda a, b: a + b, y)  # Flatten
    y = np.array(y)

    # If all ids are ints as strings, convert to ints
    if not False in [i.isdigit() for i in flat_ids]:
        flat_ids = [int(s) for s in flat_ids]

    # Extract feature set for only relevant ids
    X = dataset.get_feature_data(ids=flat_ids, features=features)

    if regularization:
        X = regularize(X, method=regularization)

    return (X, y)

def get_feature_order(dataset, features):
    """ Returns a list with the order that features requested appear in dataset """
    all_features = dataset.get_feature_names()

    i = [all_features.index(f) for f in features]
    
    return i

def classify_regions(dataset, masks, method='ERF', threshold=0.08,
                     remove_overlap=True, regularization='scale',
                     output='summary', studies=None, features=None,
                     class_weight='auto', classifier=None,
                     cross_val='4-Fold', param_grid=None, scoring='accuracy'):
    """ Perform classification on specified regions

        Given a set of masks, this function retrieves studies associated with each 
        mask at the specified threshold, optionally removes overlap and filters by studies 
        and features. Then it trains an algorithm to classify studies based on features
        and tests performance. 

        Args:
            dataset: a Neurosynth dataset
            maks: a list of paths to Nifti masks
            method: a string indicating which method to used. 
                'SVM': Support Vector Classifier with rbf kernel
                'ERF': Extremely Randomized Forest classifier
                'Dummy': A dummy classifier using stratified classes as predictor
            threshold: percentage of voxels active within the mask for study to be included
            remove_overlap: A boolean indicating if studies studies that appear in more than 
                one mask should be excluded
            regularization: A string indicating type of regularization to use. If None
                performs no regularization.
                'scale': Unit scale without demeaning
            output: A string indicating output type
                'summary': Dictionary with summary statistics including score and n
                'summary_clf': Same as above but also includes classifier 
                'clf': Only returns classifier
                Warning: using cv without grid will return an untrained classifier
            studies: An optional list of study names used to constrain the set used in
                classification. If None, will use all features in the dataset.
            features: An optional list of feature names used to constrain the set used in
                classification. If None, will use all features in the dataset.
            class_weight: Parameter to pass to classifier determining how to weight classes
            classifier: An optional sci-kit learn classifier to use instead of pre-set up 
                classifiers set up using 'method'
            cross_val: A string indicating type of cross validation to use. Can also pass a 
                scikit_classifier
            param_grid: A dictionary indicating which parameters to optimize using GridSearchCV
                If None, no GridSearch will be used

        Returns:
            A tuple (X, y) of np arrays. 
            X is a feature by studies matrix and y is a vector of class labels
    """

    (X, y) = get_studies_by_regions(dataset, masks, threshold,
                                    remove_overlap, studies, features, regularization=regularization)

    return classify(X, y, method, classifier, output, cross_val,
                    class_weight, scoring=scoring, param_grid=param_grid)


def classify(X, y, method='ERF', classifier=None, output='summary',
             cross_val=None, class_weight=None, regularization=None,
             param_grid=None, scoring='accuracy'):

    # Build classifier

    clf = Classifier(method, classifier, class_weight, param_grid)

    # Fit & test model with or without cross-validation

    if cross_val:
        score = clf.cross_val_fit(X, y, cross_val, scoring=scoring)
    else:
        # Does not support scoring function
        score = clf.fit(X, y).score(X, y)

    # Return some stuff...

    from collections import Counter
    if output == 'summary':
        return {'score': score, 'n': dict(Counter(y))}
    elif output == 'summary_clf':
        return {'score': score, 'n': dict(Counter(y)), 'clf': clf}
    elif output == 'clf':
        return clf
    else:
        pass


class Classifier:

    def __init__(self, clf_method='ERF', classifier=None,
                 class_weight=None, param_grid=None):
        """ Initialize a new classifier instance """

        # Set classifier

        if classifier is not None:
            self.clf = classifier

            from sklearn.svm import LinearSVC
            import random 
            if isinstance(self.clf, LinearSVC):
                self.clf.set_params().random_state = random.randint(0, 200)
        else:
            if clf_method == 'SVM':
                from sklearn import svm
                self.clf = svm.SVC(class_weight=class_weight)
            elif clf_method == 'ERF':
                from sklearn.ensemble import ExtraTreesClassifier
                self.clf = ExtraTreesClassifier(n_estimators=100,
                        max_depth=None, min_samples_split=1,
                        random_state=0, n_jobs=-1,
                        compute_importances=True)
            elif clf_method == 'GBC':
                from sklearn.ensemble import GradientBoostingClassifier
                self.clf = GradientBoostingClassifier(n_estimators=100,
                        max_depth=1)
            elif clf_method == 'Dummy':
                from sklearn.dummy import DummyClassifier
                self.clf = DummyClassifier(strategy='stratified')
            else:
                raise Exception('Unrecognized classification method')

        if isinstance(param_grid, dict):
            from sklearn.grid_search import GridSearchCV
            self.clf = GridSearchCV(estimator=self.clf,
                                    param_grid=param_grid, n_jobs=-1)

    def fit(self, X, y, cv=None):
        """ Fits X to outcomes y, using clf """

        # Incorporate error checking such as :
        # if isinstance(self.classifier, ScikitClassifier):
        #     do one thingNone
        # otherwiseNone.

        self.X = X
        self.y = y
        self.clf = self.clf.fit(X, y)

        return self.clf

    def cross_val_fit(self, X, y, cross_val='4-Fold', scoring='accuracy'):
        """ Fits X to outcomes y, using clf and cv_method """

        from sklearn import cross_validation

        self.X = X
        self.y = y

        # Set cross validator

        if isinstance(cross_val, basestring):
            if cross_val == '4-Fold':
                self.cver = cross_validation.StratifiedKFold(self.y, 4,
                        indices=False)

            elif cross_val == '3-Fold':
                self.cver = cross_validation.StratifiedKFold(self.y, 3,
                        indices=False)
            else:
                raise Exception('Unrecognized cross validation method')
        else:
            self.cver = cross_val

        from sklearn.grid_search import GridSearchCV
        if isinstance(self.clf, GridSearchCV):
            self.clf.set_params(cv=self.cver, scoring=scoring)

            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', category=UserWarning)
                self.clf = self.clf.fit(X, y)

            self.cvs = self.clf.best_score_
        else:
            # import warnings
            # with warnings.catch_warnings():
            #     warnings.simplefilter('ignore', category=UserWarning)
            #     self.clf.fit(X, y)

            self.cvs = cross_validation.cross_val_score(self.clf,
                    self.X, self.y, cv=self.cver, n_jobs=-1, scoring=scoring)

        return self.cvs.mean()

    def fit_dataset(self, dataset, y, features=None,
                    feature_type='features'):
        """ Given a dataset, fits either features or voxels to y """

        # Get data from dataset

        if feature_type == 'features':
            X = np.rot90(dataset.feature_table.data.toarray())
        elif feature_type == 'voxels':
            X = np.rot90(dataset.image_table.data.toarray())

        self.sk_classifier.fit(X, y)

