from pathlib import Path

import pulp as pl
import pandas as pd
solver_list = pl.listSolvers(onlyAvailable=True)

PATH = Path(__file__)


def load_bids(df):
    """
    Load bid pd.DataFrame that meets specification below.

    Parameters
    ----------
    df : pd.DataFrame
        A pd.DataFrame with the minimum fields below.

    Fields
    ----------
    PRICE : str
        The price for bid step "b".
    UNITS : :obj:`int`, optional
        The number of units linked to price for bid step "b".

    Returns
    -------
    pd.DataFrame

    Fields
    ----------
    PRICE : str
        The price for bid step "b".
    UNITS : :obj:`int`, optional
        The number of units linked to price for bid step "b".


    """

    df = (
        df.astype({'PRICE': float, 'UNITS': int})
        .sort_values(by='PRICE')
    )

    return df


def load_offers(df):
    """
    Load offer pd.DataFrame that meets specification below.

    Parameters
    ----------
    df : pd.DataFrame
        A pd.DataFrame with the minimum fields below

    Fields
    ----------
    PRICE : str
        The price for offer step "o".
    UNITS : :obj:`int`, optional
        The number of units linked to price for bid step "o".

    Returns
    -------
    pd.DataFrame

    Fields
    ----------
    PRICE : str
        The price for bid step "o".
    UNITS : :obj:`int`, optional
        The number of units linked to price for bid step "o".
    SUM_UNITS
        The sum of each group of "UNITS".
    CUMSUM_UNITS
        The cumulative sum of each group of "UNITS".
    UNCLEARED_UNITS
        The subtraction of "CUMSUM_UNITS" from "SUM_UNITS".
    """

    df = (
        df.astype({'PRICE': float, 'UNITS': int})
        .assign(SUM_UNITS=lambda x: x['UNITS'].sum())
        .sort_values(by='PRICE', ascending=True)
        .assign(CUMSUM_UNITS=lambda x: x['UNITS'].cumsum())
        .assign(UNCLEARED=lambda x: x['SUM_UNITS'] - x['CUMSUM_UNITS'])
        .sort_values(by='PRICE')
    )

    return df
