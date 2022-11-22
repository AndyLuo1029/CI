This branch is for XGBoost prediction results.

* The `xgb.py` is the Python script including model training, GridSearch and ROC-AUC plotting.

* The `DataSet.csv` is the original dataset used for prediction and validation.

* The `15Grid_result` dir includes prediction results in `.csv` file and its `ROC-AUC `plot. Its hyperparameters are determined by gridSearch in `xgb.py`.
  
  * `15_Grid_WithAUC_active_17.csv` is the result not using `organization_name` as a feature (so it just use 3 features:`'contributors_num','is_fork','use_CI'`), its ROC-AUC plot is `15_Grid.png`
  
  * `org_15_Grid_WithAUC_active_17.csv` is the result using `organization_name` as a feature (so it has 4 features). Its ROC-AUC plot is `org_15_Grid.png`

* The `CI_importance_validation` dir includes validation of used features' importance and compared whether the feature `use_CI` has considerable effects on model's AUC.
