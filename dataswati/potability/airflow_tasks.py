import pandas as pd

from .data.impute import knn_impute
from .features.build_features import build_features


def preprocessing(input_path="dataswati/data/interim/train.csv", output_path="dataswati/data/interim/train.csv"):
    df = pd.read_csv(input_path)
    df = knn_impute(df)
    df = build_features(df, interaction_features=list(df.columns), bin_features=["ph"])
    df = pd.to_csv(input_path, index=False)


if __name__ == "__main__":
    preprocessing(
        "/home/luis/Code/ODSC_AirflowK8s/AirflowKubernetes/dataswati/data/interim/train.csv",
        "/home/luis/Code/ODSC_AirflowK8s/AirflowKubernetes/dataswati/data/preprocessed/train.csv",
    )
