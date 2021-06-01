import json

import fire
import pandas as pd
from potability.models.model import PotabilityModel


def run(
    model_type: str,
    train_datapath: str,
    target_datapath: str,
    model_output_path: str,
    n_iter: int,
    n_jobs: int,
    cv: int,
):
    X = pd.read_csv(train_datapath)
    y = pd.read_csv(target_datapath)

    pm = PotabilityModel(model_type)
    best_model = pm.gridsearch(X, y, n_iter, n_jobs, cv)
    pm.save_best_model(model_output_path)
    xcom_return = {"model_output_path": model_output_path}
    with open("/airflow/xcom/return.json", "w") as file:
        json.dump(xcom_return, file)


if __name__ == "__main__":
    fire.Fire(run)
