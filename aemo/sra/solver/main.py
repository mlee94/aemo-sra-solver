import pulp as pl
import pandas as pd
solver_list = pl.listSolvers(onlyAvailable=True)

solver = pl.getSolver('PULP_CBC_CMD')

bids = pd.read_csv('../../../../auction_test_bids.csv')
offers = pd.read_csv('../../../../auction_test_offers.csv')

subset = (
    offers
    .set_index(['BIDTYPE', 'CONTRACTID', 'INTERCONNECTORID', 'FROMREGIONID'])
    .assign(SUM_QUANTITY=lambda x: x.groupby(['BIDTYPE', 'CONTRACTID', 'INTERCONNECTORID', 'FROMREGIONID'])['UNITS'].sum())
)