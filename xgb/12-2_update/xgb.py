import pandas as pd
from sklearn import preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
import numpy as np
import matplotlib.pyplot as plt
from xgboost import plot_importance
import time
import pickle
from matplotlib.pylab import rcParams



run_time = time.strftime('%m-%d_%H:%M', time.localtime())

all = pd.read_csv("DataSet.csv")

# get ci_num feature from other csv files
active_cinum = pd.read_csv("repo_active.csv")
inac_cinum = pd.read_csv("repo_inactive.csv")
temp_list = [active_cinum,inac_cinum]
ci_num = pd.concat(temp_list)
ci_num = ci_num[['repo_full_name','ci_num']]

# join two dataframes according to 'repo_full_name'
full_data = pd.merge(all,ci_num,on=['repo_full_name'],how='outer')

# drop data without ci_num (i.e. the value of ci_num is NaN)
all = full_data[~np.isnan(full_data['ci_num'])]

# get the 2020 active repo data to be the train dataset
train_active_year = "active_20"
# get 2021 active repo data to be the test set
test_active_year = "active_21"
# use 2020 active data to train the model, the label is train_res = 'active_21'
# use 2021 active data as test to check the model's accuracy, the label is predict_res = 'active_22'
train_res = test_active_year
predict_res = 'active_22'

# get all repos that are active in 2020
wait_to_split = all[all["active_20"]==True]
# split with portion 7:3 to train and test sets
X = wait_to_split[['organization_name','repo_full_name','contributors_num','is_fork','use_CI','ci_num']]
y = wait_to_split[['active_21','active_22']]

# set test portion to 0.37, since the test set will decrease after the 'active_21'== False repos are dropped
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.37, shuffle=False)

train = pd.merge(X_train,y_train,how='outer',left_index=True,right_index=True)
test = pd.merge(X_test,y_test,how='outer',left_index=True,right_index=True)
test = test[test['active_21']==True]

# get the ground truth from dataset to use to check the model's accuracy
ground_truth = test[predict_res]
# change bool to int
ground_truth = ground_truth.astype(int)

# get the repo names
# test_cop = test['repo_full_name']

# no empty data in dataset, no need to fill 
# print(train[train.isnull().T.any()])
# print(test[test.isnull().T.any()])

# change string to lable
for f in train.columns:
    if train[f].dtype=='object':
        # print(f)
        lbl = preprocessing.LabelEncoder()
        train[f] = lbl.fit_transform(list(train[f].values))
for f in test.columns:
    if test[f].dtype == 'object':
        # print(f)
        lbl = preprocessing.LabelEncoder()
        test[f] = lbl.fit_transform(list(test[f].values))


# choose feature to be used in prediction
# feature_columns_to_use = ['organization_name','contributors_num','is_fork','use_CI','ci_num'] # succeed
# feature_columns_to_use = ['organization_name','contributors_num','is_fork','use_CI'] # failed
# feature_columns_to_use = ['organization_name','contributors_num','is_fork','ci_num']
# feature_columns_to_use = ['organization_name','contributors_num','is_fork'] # failed

# feature_columns_to_use = ['contributors_num','is_fork','use_CI','ci_num'] # succeed,AUC: Tuned 0.6475714957912898 Default: 0.642204363315881
# feature_columns_to_use = ['contributors_num','is_fork','use_CI'] # succeed,AUC: Tuned 0.6324686867479778 Default 0.6264166585753872
# feature_columns_to_use = ['contributors_num','is_fork','ci_num'] # succeed,AUC: Tuned 0.6450619543054321 Default 0.6436854409249453
# feature_columns_to_use = ['contributors_num','is_fork'] # succeed,AUC: Tuned 0.6440932414163971 Default 0.637534823622553

model = XGBClassifier(
    learning_rate= 0.1,
    n_estimators= 1000,
    max_depth= 5,
    # min_child_weight= 1,
    gamma=0,
    subsample= 0.8,
    colsample_bytree=0.8,
    objective= 'binary:logistic',
    scale_pos_weight=1,
    seed=27
)

big_train = train[feature_columns_to_use]
big_test = test[feature_columns_to_use]
train_X = big_train.to_numpy()
test_X = big_test.to_numpy()
# the label for train data
train_y = train[train_res]

# tune hyper param
# Step1: tune estimators_num

rcParams['figure.figsize'] = 8, 8
train_target = train_res
test_target = predict_res
predictors = feature_columns_to_use

def modelfit(alg, dtrain, dtest, predictors, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):

    if useTrainCV:
        xgb_param = alg.get_xgb_params()
        xgtrain =xgb.DMatrix(dtrain[predictors].values, label=dtrain[train_target].values)
        cvresult =xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
        metrics='auc', early_stopping_rounds=early_stopping_rounds)
        
        # print(cvresult)
        print("Best estimateor num is:"+str(cvresult.shape[0]))
        alg.set_params(n_estimators=cvresult.shape[0])

        #Fit the algorithm on the data
        alg.fit(dtrain[predictors], dtrain[train_target],eval_metric='auc') 
        
        #Predict training set:
        dtrain_predictions = alg.predict(dtrain[predictors])
        dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]

        #Predict test set:
        dtest_predictions = alg.predict(dtest[predictors])
        dtest_predprob = alg.predict_proba(dtest[predictors])[:,1]
        
        #Print model report:
        print("\nModel Report")
        print("Accuracy :%.4g" % metrics.accuracy_score(dtrain[train_target].values, dtrain_predictions))
        print("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain[train_target], dtrain_predprob))
        print("AUC Score (Test): %f" % metrics.roc_auc_score(dtest[test_target], dtest_predprob))
        # print(alg.get_params())
        
        # default: scoring feature with "weight"
        '''
        How the importance is calculated: either “weight”, “gain”, or “cover”
        ”weight” is the number of times a feature appears in a tree
        ”gain” is the average gain of splits which use the feature
        ”cover” is the average coverage of splits which use the feature where coverage is defined as the number of samples affected by the split
        '''
        feat_imp = pd.Series(alg.get_booster().get_fscore()).sort_values(ascending=False)
        # print(feat_imp)
        feat_imp.plot(kind='bar',title='Feature Importances')
        plt.ylabel('Feature Importance Score') 
        # plt.show()
        return cvresult.shape[0]

train_col = predictors.copy()
test_col = predictors.copy()
train_col.append(train_res)
test_col.append(predict_res)
# print(train_col)
# print(test_col)
dtrain = train[train_col]
dtest = test[test_col]

# estimators_num = modelfit(model, dtrain, dtest, predictors)
'''
Model Report
Accuracy :0.7377
AUC Score (Train): 0.712982
AUC Score (Test): 0.642750
'''
estimators_num = 15


# Step2: tune max_depth and min_child_weight
param_test1 = {
# 'max_depth':range(3,10,2),
# 'min_child_weight':range(1,6,2)
'max_depth':[4,5,6],
# 'min_child_weight':[0.001,0.01,0.05,0.1]
}
gsearch1 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=estimators_num, max_depth=5,
# min_child_weight=1, 
gamma=0, subsample=0.8, colsample_bytree=0.8,
objective= 'binary:logistic', scale_pos_weight=1, seed=27), 
param_grid = param_test1, scoring='roc_auc',n_jobs=-1, cv=5)

# gsearch1.fit(dtrain[predictors],dtrain[train_target])
# print(gsearch1.best_params_, gsearch1.best_score_)


# {'max_depth': 4} 0.7016331253643807

best_dp = 4
# best_mcw = 1


# Step3: tune gamma
param_test3 = {
'gamma':[0.18,0.20,0.22]
# 'gamma':[i/10.0 for i in range(0,5)]
}
gsearch3 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=estimators_num, max_depth=best_dp,
# min_child_weight=best_mcw, 
gamma=0, subsample=0.8, colsample_bytree=0.8,
objective= 'binary:logistic', scale_pos_weight=1,seed=27), 
param_grid = param_test3, scoring='roc_auc', cv=5)

# gsearch3.fit(dtrain[predictors],dtrain[train_target])
# print(gsearch3.best_params_, gsearch3.best_score_)
# for i in ['mean_test_score', 'std_test_score', 'params']:
#     print(i," : ",gsearch3.cv_results_[i])


best_gamma = 0.2
# {'gamma': 0.2} 0.7016941690378609

# re-calibrate

model2 = XGBClassifier(
    learning_rate= 0.1,
    n_estimators= 1000,
    max_depth= best_dp,
    # min_child_weight= best_mcw,
    gamma=best_gamma,
    subsample= 0.8,
    colsample_bytree=0.8,
    objective= 'binary:logistic',
    scale_pos_weight=1,
    seed=27
)

# modelfit(model2, dtrain, dtest, predictors)
estimators_num = 13
'''
Model Report
Accuracy :0.7382
AUC Score (Train): 0.710632
AUC Score (Test): 0.646471
'''


# Step4: Tune subsample and colsample_bytree
param_test4 = {
'colsample_bytree':[i/100.0 for i in range(55,70,5)],
'subsample':[i/100.0 for i in range(75,90,5)],
# 'subsample':[i/10.0 for i in range(6,10)],
# 'colsample_bytree':[i/10.0 for i in range(6,10)]
}
gsearch4 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=estimators_num, max_depth=best_dp,
#  min_child_weight=best_mcw,
  gamma=best_gamma, subsample=0.8, colsample_bytree=0.8,
 objective= 'binary:logistic', scale_pos_weight=1,seed=27), 
 param_grid = param_test4, scoring='roc_auc', cv=5)

# gsearch4.fit(dtrain[predictors],dtrain[train_target])
# print(gsearch4.best_params_, gsearch4.best_score_)


# {'colsample_bytree': 0.55, 'subsample': 0.85} 0.7016646600708313
best_colsamplebytree = 0.55
best_subsample = 0.85


# Step5: tune reg_alpha and reg_lambda
param_test6 = {
'reg_alpha':[0.1,0.5,1.0,1.5],
'reg_lambda':[1e-02,1e-05,1e-04]
# 'reg_alpha':[1e-5, 1e-2, 0.1, 1, 100],
# 'reg_lambda':[1e-5, 1e-2, 0.1, 1, 100]
}
gsearch6 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=estimators_num, max_depth=best_dp,
#  min_child_weight=best_mcw, 
 gamma=best_gamma, subsample=best_subsample, colsample_bytree=best_colsamplebytree,
 objective= 'binary:logistic', scale_pos_weight=1,seed=27), 
 param_grid = param_test6, scoring='roc_auc', cv=5)

# gsearch6.fit(dtrain[predictors],dtrain[train_target])
# print(gsearch6.best_params_, gsearch6.best_score_)

# {'reg_alpha': 1.0, 'reg_lambda': 1e-05} 0.7035187163355696
best_reg_alpha = 1
best_reg_lambda = 1e-5

# re-calibrate

model3 = XGBClassifier(
    learning_rate= 0.1,
    n_estimators= 1000,
    max_depth= best_dp,
    # min_child_weight= best_mcw,
    gamma=best_gamma,
    subsample= best_subsample,
    colsample_bytree=best_colsamplebytree,
    reg_alpha = best_reg_alpha,
    reg_lambda = best_reg_lambda,
    objective= 'binary:logistic',
    scale_pos_weight=1,
    seed=27
)

# modelfit(model3, dtrain, dtest, predictors)

'''
Model Report
Accuracy :0.7473
AUC Score (Train): 0.735942
AUC Score (Test): 0.654727
'''

# Step6: Reducing Learning Rate and add more trees

model4 = XGBClassifier(
    learning_rate= 0.01,
    n_estimators= 1000,
    max_depth= best_dp,
    # min_child_weight= best_mcw,
    gamma=best_gamma,
    subsample= best_subsample,
    colsample_bytree=best_colsamplebytree,
    reg_alpha = best_reg_alpha,
    reg_lambda = best_reg_lambda,
    objective= 'binary:logistic',
    scale_pos_weight=1,
    seed=27
)

# modelfit(model4, dtrain, dtest, predictors)
# update estimator_num
estimators_num = 5
'''
Model Report
Accuracy :0.7145
AUC Score (Train): 0.707142
AUC Score (Test): 0.644093
'''

# Test if default hyper params perform better
# modelfit(model, dtrain, dtest, predictors)
'''
Model Report
Accuracy :0.7511
AUC Score (Train): 0.748811
AUC Score (Test): 0.655139
'''

# get the final tuned model
final_model = XGBClassifier(
    learning_rate= 0.01,
    n_estimators= estimators_num,
    max_depth= best_dp,
    # min_child_weight= best_mcw,
    gamma=best_gamma,
    subsample= best_subsample,
    colsample_bytree=best_colsamplebytree,
    reg_alpha = best_reg_alpha,
    reg_lambda = best_reg_lambda,
    objective= 'binary:logistic',
    scale_pos_weight=1,
    seed=27
)




# get tuned model and default model feature importance and AUC

# default
model.fit(train_X, train_y)
default_predictions = model.predict(test_X)
default_predic_prob = model.predict_proba(test_X)

# tuned
final_model.fit(train_X, train_y)
tune_predictions = final_model.predict(test_X)
tune_predic_prob = final_model.predict_proba(test_X)

model.get_booster().feature_names = feature_columns_to_use
final_model.get_booster().feature_names = feature_columns_to_use
default_feat_imp = pd.Series(model.get_booster().get_fscore()).sort_values(ascending=False)
tune_feat_imp = pd.Series(final_model.get_booster().get_fscore()).sort_values(ascending=False)
print('default')
print(default_feat_imp)
print('tuned')
print(tune_feat_imp)
for i in ['learning_rate', 'n_estimators', 'max_depth','min_child_weight','gamma','subsample','colsample_bytree','reg_alpha','reg_lambda','scale_pos_weight','seed']:
    print(i,"=",final_model.get_params()[i])
default_feat_imp.plot(kind='bar',title='Default Feature Importances')
plt.ylabel('Feature Importance Score') 
plt.show()
tune_feat_imp.plot(kind='bar',title='Tuned Feature Importances')
plt.ylabel('Feature Importance Score') 
plt.show()
# plt.savefig('CI_num/FeatureImportance_'+str(run_time)+".PNG")

y_truth = ground_truth.to_numpy()

# ROC-AUC part
def ROC_AUC(predic_prob, title):
    global y_truth
    fpr, tpr, thresholds = metrics.roc_curve(y_truth, predic_prob[:,1])
    roc_auc = metrics.auc(fpr, tpr)
    display = metrics.RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name=title)
    auc_value = metrics.roc_auc_score(y_truth, predic_prob[:,1])
    print(title+":"+str(auc_value))
    display.plot()
    # plt.savefig('CI_num/ROC_'+str(run_time)+".PNG")
    plt.show()
ROC_AUC(default_predic_prob,"Default Model")
ROC_AUC(tune_predic_prob,"Tuned Model")





# # '''
# # # export result as csv

# # # increase its dimension to make it can concatenate with other ndarry
# # predictions = predictions[:, None]
# # reponame = test_cop.to_numpy()
# # reponame = reponame[:, None]
# # # truth is from original dataset, 100% valid, use for checking the accuracy of model
# # truth = ground_truth.to_numpy()
# # truth = truth[:, None]

# # # print(truth)
# # # print(truth.shape)

# # # print(reponame)
# # # print(reponame.shape)

# # # print(predictions)
# # # print(predictions.shape)

# # res = np.concatenate((reponame, predictions,truth),axis=1)
# # # print(res)
# # # print(res.shape)

# # results = pd.DataFrame(res,columns=['repo_full_name','predict','Truth'])
# # # increase new col to indicate whether the prediction of specific repo is accurate
# # results['correct'] = results.apply(lambda x: 1 if x.predict == x.Truth else 0,axis=1)

# # results.to_csv("preRes/test_Grid_WithAUC_"+predict_res+".csv",index=False)
# # '''