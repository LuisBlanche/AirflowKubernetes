import logging

import numpy as np
from interpret.glassbox import ExplainableBoostingClassifier
from lightgbm import LightGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV


class PotabilityModel:
    def __init__(self, model: str) -> None:
        if model == "interpret":
            self.model = ExplainableBoostingClassifier()
        elif model == "rf":
            self.model = RandomForestClassifier()
        elif model == "lightgbm":
            self.model = LightGBMClassifier()

    def __repr__(self) -> str:
        return f"This a {self.model} model"

    def gridsearch(self, X, y, n_iter=100, n_jobs=1, cv=3):
        random_grid = self._get_random_grid_search()
        rscv = RandomizedSearchCV(
            estimator=self.model, param_distributions=random_grid, n_iter=n_iter, cv=cv, verbose=2, n_jobs=n_jobs
        )
        rscv.fit(X, y)
        logging.info(f"Best score for {self.model} : {rscv.best_score_} ")
        self.best_params = rscv.best_params_
        self.best_cv_model = rscv.best_estimator_

    def fit(self, X, y):
        self.best_cv_model.fit(X, y)

    def predict(self, X):
        self.best_cv_model.predict(X)

    def _get_random_grid_search(self):
        # RF
        n_estimators = [int(x) for x in np.linspace(start=20, stop=150, num=10)]
        max_features = ["auto", "sqrt"]
        max_depth = [int(x) for x in np.linspace(4, 30, num=11)]
        min_samples_split = [2, 5, 10]
        min_samples_leaf = [1, 2, 4]
        bootstrap = [True, False]
        # LightGBM
        learning_rate = np.random.uniform(0, 1)
        boosting_type = np.random.choice(["gbdt", "dart", "goss"])
        sub_feature = np.random.uniform(0, 1)
        num_leaves = [int(x) for x in np.linspace(20, 300, num=10)]
        min_data = [int(x) for x in np.linspace(10, 110, num=11)]
        # ExplainableBoosting
        max_bins = [int(x) for x in np.linspace(start=128, stop=1024, num=6)]
        binning = ["uniform", "quantile", "quantile_humanized"]
        interactions = [int(x) for x in np.linspace(10, 110, num=11)]
        max_rounds = [int(x) for x in np.linspace(start=1000, stop=6000, num=10)]
        if self.model == "rf":
            return {
                "n_estimators": n_estimators,
                "max_features": max_features,
                "max_depth": max_depth,
                "min_samples_split": min_samples_split,
                "min_samples_leaf": min_samples_leaf,
                "bootstrap": bootstrap,
            }
        elif self.model == "lightgbm":
            return {
                "learning_rate": learning_rate,
                "boosting_type": boosting_type,
                "sub_feature": sub_feature,
                "num_leaves": num_leaves,
                "min_data": min_data,
                "max_depth": max_depth,
            }
        elif self.model == "interpret":
            return {
                "learning_rate": learning_rate,
                "max_bins": max_bins,
                "min_samples_leaf": min_samples_leaf,
                "binning": binning,
                "interactions": interactions,
                "max_rounds": max_rounds,
            }
