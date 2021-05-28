import pandas as pd
import fire
from potability.models.model import PotabilityModel


def run(model_type: str, train_datapath: str, target_datapath: str, model_output_path: str, n_iter: int, n_jobs: int, cv: int ):
    X = pd.read_csv(train_datapath)
    y = pd.read_csv(target_datapath)

    pm = PotabilityModel(model_type)
    best_model = pm.gridsearch(X, y, n_iter, n_jobs, cv)
    pm.save_best_model(model_output_path)


if __name__=='__main__':
    fire.Fire(run)