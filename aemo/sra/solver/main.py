import pulp as pl
import pandas as pd
solver_list = pl.listSolvers(onlyAvailable=True)

from data import (
    load_bids,
    load_offers
)


def solve(bids, offers):
    """
    Run pulp open source LP solver according to AEMO's Settlement Residue Auction's design (excluding linked bids).

    This is an integer programming problem.

    Parameters
    ----------
    bids : pd.DataFrame
        Returned by `data.load_bids`.

    offers : pd.DataFrame
        Returned by `data.load_offers`.

    """

    pl.getSolver('PULP_CBC_CMD')
    mdl = pl.LpProblem('SRA-Solve', sense=pl.LpMaximize)

    # Parameters
    available_offer_units = offers.get('UNITS').reset_index(drop=True).to_dict()
    offer_price = offers.get('PRICE').reset_index(drop=True).to_dict()
    offer_index = list(available_offer_units.keys())

    available_bid_units = bids.get('UNITS').reset_index(drop=True).to_dict()
    bid_price = bids.get('PRICE').reset_index(drop=True).to_dict()
    bid_index = list(available_bid_units.keys())

    # Variables
    uncleared_offers = pl.LpVariable.dicts(
        indices=offer_index, lowBound=0, upBound=None, cat=pl.LpInteger, name='uncleared_offers',
    )
    cleared_bids = pl.LpVariable.dicts(
        indices=bid_index, lowBound=0, upBound=None, cat=pl.LpInteger, name='cleared_bids',
    )

    # Constraints
    mdl.addConstraint(
        pl.lpSum([uncleared_offers[i] for i in offer_index]) <= pl.lpSum([available_offer_units[i] for i in offer_index])
        - pl.lpSum([cleared_bids[i] for i in bid_index])
    )
    for i in offer_index:
        mdl.addConstraint(uncleared_offers[i] <= available_offer_units[i], name=f'uncleared_offer_limit{i}')
    for i in bid_index:
        mdl.addConstraint(cleared_bids[i] <= available_bid_units[i], name=f'cleared_bid_limit{i}')

    uncleared_offer_value = sum(uncleared_offers[i] * offer_price[i] for i in offer_index)
    cleared_bid_value = sum(cleared_bids[i] * bid_price[i] for i in bid_index)

    # Set objective function
    mdl.setObjective(cleared_bid_value + uncleared_offer_value)

    # Optimize
    mdl.solve()

    # Summarise
    final_uncleared_offers = {i: int(uncleared_offers[i].value()) for i in offer_index}
    final_cleared_bids = {i: int(cleared_bids[i].value()) for i in bid_index}

    total_cleared_bids = sum(final_cleared_bids.values())
    total_uncleared_offers = sum(final_uncleared_offers.values())
    total_objective = cleared_bid_value.value() + uncleared_offer_value.value()

    print(f"Uncleared Offer Quantity: {total_uncleared_offers}")
    print(f"Cleared Bids: {total_cleared_bids}")
    print(f"Objective: {total_objective}")


    # Run optimisation again to solve for cleared price (ie. shadow price/lagrangian multiplier from energy balance constraint)
    mdl = pl.LpProblem('SRA-Solve-2', sense=pl.LpMaximize)

    # Constraints
    mdl.addConstraint(
        pl.lpSum([uncleared_offers[i] for i in offer_index]) + 1 <= pl.lpSum([available_offer_units[i] for i in offer_index])
        - pl.lpSum([cleared_bids[i] for i in bid_index])
    )
    for i in offer_index:
        mdl.addConstraint(uncleared_offers[i] <= available_offer_units[i], name=f'uncleared_offer_limit{i}')
    for i in bid_index:
        mdl.addConstraint(cleared_bids[i] <= available_bid_units[i], name=f'cleared_bid_limit{i}')

    uncleared_offer_value = sum(uncleared_offers[i] * offer_price[i] for i in offer_index)
    cleared_bid_value = sum(cleared_bids[i] * bid_price[i] for i in bid_index)

    # Set objective function
    mdl.setObjective(cleared_bid_value + uncleared_offer_value)

    # Optimize
    mdl.solve()

    # Solved twice for illustrative purposes only - price can be retrieved using duals instead.
    
    new_objective = cleared_bid_value.value() + uncleared_offer_value.value()

    clearing_price = round(total_objective - new_objective, 2)

    if clearing_price in offer_price.values():
        setter = 'OFFER'
    elif clearing_price in bid_price.values():
        setter = 'BID'
    else:
        setter = None

    print(f"Clearing Price: ${clearing_price}; set by {setter}")
    columns = ['Cleared Bids', 'Uncleared Offers', 'Default Units', 'Clearing Price', 'Objective']
    primary_allocation = offers.query('PRICE == 0').get('UNITS')[0]
    summary_df = (
        pd.DataFrame([
            [total_cleared_bids, total_uncleared_offers, primary_allocation, clearing_price, total_objective]
        ], columns=columns)
    )
    return summary_df
