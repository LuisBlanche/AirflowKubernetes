import logging

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
    use_interactions: bool = True,
):
    logging.info(f"Reading training data from {train_datapath}")
    logging.info(f"Reading target data from {target_datapath}")
    X = pd.read_csv(train_datapath)

    y = pd.read_csv(target_datapath)

    pm = PotabilityModel(model_type, model_output_path, use_interactions)
    _ = pm.gridsearch(X, y, n_iter, n_jobs, cv)
    pm.save_best_model()
    logging.info(f"Model saved in: {pm.model_path}")


if __name__ == "__main__":
    fire.Fire(run)
