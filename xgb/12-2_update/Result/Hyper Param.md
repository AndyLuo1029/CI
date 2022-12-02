* F1: 'contributors_num','is_fork','use_CI','ci_num'
  
  * feature imp
    
    > default
    > contributors_num    9668.0
    > ci_num              4358.0
    > use_CI              1514.0
    > is_fork              122.0
    > dtype: float64
    > 
    > tuned
    > contributors_num    27.0
    > ci_num              15.0
    > use_CI               3.0
    > is_fork              2.0
    > dtype: float64
  
  * model
    
    > learning_rate = 0.01
    > n_estimators = 5
    > max_depth = 4
    > min_child_weight = 1
    > gamma = 0.28
    > subsample = 0.8
    > colsample_bytree = 0.55
    > reg_alpha = 0
    > reg_lambda = 0.1
    > scale_pos_weight = 1
    > seed = 27
  
  * auc
    
    > Default Model:0.642204363315881
    > Tuned Model:0.6475714957912898

* F2:'contributors_num','is_fork','use_CI'
  
  * feature imp
    
    > default
    > contributors_num    8891.0
    > use_CI              1263.0
    > is_fork              422.0
    > dtype: float64
    > tuned
    > contributors_num    138.0
    > use_CI               37.0
    > is_fork              29.0
    > dtype: float64
  
  * model
    
    > learning_rate = 0.01
    > n_estimators = 32
    > max_depth = 5
    > min_child_weight = 1
    > gamma = 0.18
    > subsample = 0.95
    > colsample_bytree = 0.7
    > reg_alpha = 1
    > reg_lambda = 0.1
    > scale_pos_weight = 1
    > seed = 27
  
  * auc
    
    > Default Model:0.6264166585753872
    > Tuned Model:0.6324686867479778

* F3:'contributors_num','is_fork','ci_num'
  
  * feature imp
    
    > default
    > contributors_num    8333.0
    > ci_num              4237.0
    > is_fork              147.0
    > dtype: float64
    > tuned
    > contributors_num    481.0
    > ci_num              374.0
    > is_fork               2.0
    > dtype: float64
  
  * model
    
    > learning_rate = 0.01
    > n_estimators = 312
    > max_depth = 2
    > min_child_weight = 1
    > gamma = 0.4
    > subsample = 0.8
    > colsample_bytree = 0.7
    > reg_alpha = 0.1
    > reg_lambda = 10
    > scale_pos_weight = 1
    > seed = 27
  
  * auc
    
    > Default Model:0.6436854409249453
    > Tuned Model:0.6450619543054321

* F4:'contributors_num','is_fork'
  
  * feature imp
    
    > default
    > contributors_num    6975.0
    > is_fork              468.0
    > dtype: float64
    > tuned
    > contributors_num    16.0
    > dtype: float64
  
  * model
    
    > learning_rate = 0.01
    > n_estimators = 5
    > max_depth = 4
    > min_child_weight = 1
    > gamma = 0.2
    > subsample = 0.85
    > colsample_bytree = 0.55
    > reg_alpha = 1
    > reg_lambda = 1e-05
    > scale_pos_weight = 1
    > seed = 27
  
  * auc
    
    > Default Model:0.637534823622553
    > Tuned Model:0.6440932414163971
