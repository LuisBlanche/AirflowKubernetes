from typing import List

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
    df = build_interaction_features(df, interaction_features)
    df = quantile_binning(df, bin_features)
    return df


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
    df[colnames] = interactions
    return df


def quantile_binning(
    df: pd.DataFrame,
    bin_features: List,
    quantile_list=[0, 0.25, 0.5, 0.75, 1.0],
    quantile_labels: List = ["0-25Q", "25-50Q", "50-75Q", "75-100Q"],
    as_dummies: bool = False,
):
    for feature in bin_features:
        quantiles = pd.qcut(df[feature], q=quantile_list, labels=quantile_labels)

        if as_dummies is True:
            dummies = pd.get_dummies(quantiles, prefix=feature)
            return df.join(dummies)
        else:
            return df.join(quantiles)
