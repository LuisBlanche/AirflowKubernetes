import logging
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
from interpret.glassbox import ExplainableBoostingClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, f1_score, plot_confusion_matrix
from sklearn.model_selection import RandomizedSearchCV


class PotabilityModel:
    def __init__(self, model_type: str, model_path: str) -> None:
        self.model_type = model_type
        self.model_path = Path(model_path) / self.model_type
        self.model_path.mkdir(parents=True, exist_ok=True)
        if model_type == "interpret":
            self.initial_model = ExplainableBoostingClassifier()
        elif model_type == "rf":
            self.initial_model = RandomForestClassifier()
        elif model_type == "lightgbm":
            self.initial_model = LGBMClassifier()

    def __repr__(self) -> str:
        return f"This a {self.model_type} model"

    def gridsearch(self, X, y, n_iter=100, n_jobs=1, cv=3):
        random_grid = self._get_random_grid_search()
        rscv = RandomizedSearchCV(
            estimator=self.initial_model,
            param_distributions=random_grid,
            n_iter=n_iter,
            cv=cv,
            verbose=2,
            n_jobs=n_jobs,
        )
        rscv.fit(X, y.values.ravel())
        logging.info(f"Best score for {self.model_type} : {rscv.best_score_} ")
        self.best_params = rscv.best_params_
        self.best_cv_model = rscv.best_estimator_

    def fit(self, X, y):
        self.best_cv_model.fit(X, y)

    def save_best_model(self):
        joblib.dump(self, self.model_path / {self.model_type} / "potability.joblib")

    def predict(self, X):
        return self.best_cv_model.predict(X)

    def evaluate(self, X_test, y_test):
        y_pred = self.predict(X_test)
        print(f"Model accuracy = {accuracy_score(y_test.values, y_pred)}")
        print(f"Model F1 Score= {f1_score(y_test.values, y_pred)}")
        plot_confusion_matrix(self.best_cv_model, X_test, y_test)

        plt.savefig(self.model_path / "confusion_matrix.png")
        self.save_feature_importance(X_test, y_test, self.model_path)

    def save_feature_importance(self, X_test, y_test):

        result = permutation_importance(self.best_cv_model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=2)
        sorted_idx = result.importances_mean.argsort()
        fig, ax = plt.subplots()
        ax.boxplot(result.importances[sorted_idx].T, vert=False, labels=X_test.columns[sorted_idx])
        ax.set_title("Permutation Importances (test set)")
        fig.tight_layout()
        plt.savefig(self.model_path / "feature_importance.png")
        if self.model_type == "interpret":
            ebm_global = self.best_cv_model.explain_global()
            for i, feature in enumerate(X_test.columns):
                ebm_global.visualize(i).write_html(self.model_path / f"{feature}.html")

    def _get_random_grid_search(self):
        # RF
        n_estimators = [int(x) for x in np.linspace(start=10, stop=200, num=10)]
        max_features = ["auto", "sqrt"]
        max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
        min_samples_split = [2, 5, 10]
        min_samples_leaf = [1, 2, 4]
        bootstrap = [True, False]
        # LightGBM
        learning_rate = [x for x in np.linspace(0.01, 1, num=10)]
        boosting_type = ["gbdt", "dart", "goss"]
        sub_feature = [x for x in np.linspace(0.01, 1, num=10)]
        num_leaves = [int(x) for x in np.linspace(20, 300, num=10)]
        min_data = [int(x) for x in np.linspace(10, 110, num=11)]
        # ExplainableBoosting
        max_bins = [int(x) for x in np.linspace(start=128, stop=1024, num=6)]
        binning = ["uniform", "quantile", "quantile_humanized"]
        interactions = [int(x) for x in np.linspace(10, 110, num=11)]

        if self.model_type == "rf":
            return {
                "n_estimators": n_estimators,
                "max_features": max_features,
                "max_depth": max_depth,
                "min_samples_split": min_samples_split,
                "min_samples_leaf": min_samples_leaf,
                "bootstrap": bootstrap,
            }
        elif self.model_type == "lightgbm":
            return {
                "learning_rate": learning_rate,
                "boosting_type": boosting_type,
                "sub_feature": sub_feature,
                "num_leaves": num_leaves,
                "min_data": min_data,
                "max_depth": max_depth,
            }
        elif self.model_type == "interpret":
            return {
                "learning_rate": learning_rate,
                "max_bins": max_bins,
                "min_samples_leaf": min_samples_leaf,
                "binning": binning,
                "interactions": interactions,
                "max_rounds": [int(x) for x in np.linspace(start=1000, stop=6000, num=10)],
            }
