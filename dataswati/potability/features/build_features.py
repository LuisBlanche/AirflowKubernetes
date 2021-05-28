from typing import List
import logging
import fire 
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures


def build_features(df: pd.DataFrame, interaction_features: List, bin_features: List) -> pd.DataFrame:
    """Add feature to df

    Args:
        df (pd.DataFrame): dataframe
        interaction_features (List): List of feature to take into consideration for interaction
        bin_features (List): List of features to bin

    Returns:
        pd.DataFrame: df with more features
    """
    features = build_interaction_features(df, interaction_features)
    features = quantile_binning(features, bin_features)
    return features 


def build_interaction_features(df: pd.DataFrame, interaction_features: List) -> pd.DataFrame:
    pf = PolynomialFeatures(interaction_only=True, include_bias=False)
    interactions = pf.fit_transform(df[interaction_features])
    colnames = []
    for row in pf.powers_[
        :,
    ]:
        if sum(row) == 1:
            colnames.append(interaction_features[np.argmax(row)])
        else:
            colnames.append(" * ".join([interaction_features[i] for i, x in enumerate(list(row)) if x == 1]))
    logging.info(f"Adding columns {colnames}")
    df[colnames] = interactions

    return df


def quantile_binning(
    df: pd.DataFrame,
    bin_features: List,
    quantile_list=[0, 0.25, 0.5, 0.75, 1.0],
    quantile_labels: List = [1, 2, 3, 4],
    as_dummies: bool = False,
):
    for feature in bin_features:
        quantiles = pd.qcut(df[feature], q=quantile_list, labels=quantile_labels)

        if as_dummies is True:
            dummies = pd.get_dummies(quantiles, prefix=feature)
            df =  df.join(dummies)
        else:
            df = df.join(quantiles, rsuffix='_quantiles')
    return df 


def run(input_path: str, 
        output_path: str,
        interaction_features: List=["ph","Hardness","Solids","Chloramines","Sulfate","Conductivity","Organic_carbon","Trihalomethanes","Turbidity"], 
        bin_features: List=["ph","Hardness","Solids","Chloramines","Sulfate","Conductivity","Organic_carbon","Trihalomethanes","Turbidity"]): 
    df = pd.read_csv(input_path)
    df = build_features(df, interaction_features, bin_features)
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    fire.Fire(run)