import pandas as pd
from sklearn import preprocessing
from sklearn import metrics
import xgboost as xgb
import numpy as np
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

all = pd.read_csv("DataSet.csv")

# get the 2015 active repo data to be the train dataset
train_active_year = "active_15"
# get 2016 active repo data to be the test set
test_active_year = "active_16"
# use 2015 active data(all_15) to train the model, the label is train_res = 'active_16'
# use 2016 active data(all_16) as test to check the model's accuracy, the label is predict_res = 'active_17'
train_res = test_active_year
predict_res = 'active_17'

# we can only use repos that are active in chosen year, since only these data are valid
train = all[all[train_active_year]==True]
test = all[all[test_active_year]==True]

# get the ground truth from dataset to use to check the model's accuracy
ground_truth = test[predict_res]
# change bool to int
ground_truth = ground_truth.astype(int)

# get the repo names
test_cop = test['repo_full_name']

# no empty data in dataset, no need to fill 
# print(train[train.isnull().T.any()])
# print(test[test.isnull().T.any()])

# change string to lable
for f in train.columns:
    if train[f].dtype=='object':
        print(f)
        lbl = preprocessing.LabelEncoder()
        train[f] = lbl.fit_transform(list(train[f].values))
for f in test.columns:
    if test[f].dtype == 'object':
        print(f)
        lbl = preprocessing.LabelEncoder()
        test[f] = lbl.fit_transform(list(test[f].values))

# choose feature to be used in prediction
feature_columns_to_use = ['organization_name','contributors_num','is_fork','use_CI']
# feature_columns_to_use = ['contributors_num','is_fork','use_CI']

big_train = train[feature_columns_to_use]
big_test = test[feature_columns_to_use]
train_X = big_train.to_numpy()
test_X = big_test.to_numpy()
# the label for train data
train_y = train[train_res]

model = xgb.XGBClassifier(
# below is gridSearched best hyperparams
        colsample_bytree=0.5,
        learning_rate=0.11473684210526315,
        max_depth= 3,
        min_child_weight= 7,
        n_estimators= 100,
        subsample= 0.7,
)

'''
# GridSearch part
parameters = {
    'max_depth': [3, 5, 6, 7, 9, 12],
    'n_estimators': range(100,200,20),
    'learning_rate': np.linspace(0.01,2,20),
    'subsample': [0.6, 0.7, 0.8, 0.85, 0.95],
    'colsample_bytree': [0.5, 0.6, 0.7, 0.8, 0.9],
    'min_child_weight': [1, 3, 5, 7],
}

# 有了gridsearch我们便不需要fit函数
grid = GridSearchCV(model, param_grid=parameters, cv=3, scoring='accuracy', n_jobs=-1)
grid.fit(train_X, train_y)

print("Best score: %0.3f" % grid.best_score_)
print("Best parameters set:")
best_parameters = grid.best_estimator_.get_params()
best_estimator = grid.best_estimator_
print(best_estimator)
for param_name in sorted(parameters.keys()):
    print("\t%s: %r" % (param_name, best_parameters[param_name]))
'''

# training model with 2015 active repos and their status in 2016
model.fit(train_X, train_y)

# use model to predict 2016 active repos whether are active in 2017
predictions = model.predict(test_X)
# predictions = best_estimator.predict(test_X)

predic_prob = model.predict_proba(test_X)

y_truth = ground_truth.to_numpy()

# ROC-AUC part
fpr, tpr, thresholds = metrics.roc_curve(y_truth, predic_prob[:,1])
roc_auc = metrics.auc(fpr, tpr)
display = metrics.RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name='xbg estimator')
display.plot()
plt.show()


# export result as csv

# increase its dimension to make it can concatenate with other ndarry
predictions = predictions[:, None]
reponame = test_cop.to_numpy()
reponame = reponame[:, None]
# truth is from original dataset, 100% valid, use for checking the accuracy of model
truth = ground_truth.to_numpy()
truth = truth[:, None]

# print(truth)
# print(truth.shape)

# print(reponame)
# print(reponame.shape)

# print(predictions)
# print(predictions.shape)

res = np.concatenate((reponame, predictions,truth),axis=1)
# print(res)
# print(res.shape)

results = pd.DataFrame(res,columns=['repo_full_name','predict','Truth'])
# increase new col to indicate whether the prediction of specific repo is accurate
results['correct'] = results.apply(lambda x: 1 if x.predict == x.Truth else 0,axis=1)

results.to_csv("preRes/org_15_Grid_WithAUC_"+predict_res+".csv",index=False)
