from .defi_llama import Defillama
from .dune_service import DuneService
from .mantle_api import MantleAPI


class DataSource(Defillama, DuneService, MantleAPI):
    def __init__(self):
        Defillama.__init__(self)
        DuneService.__init__(self)
        MantleAPI.__init__(self)




# source = DataSource()

""" portfolio analysis of an address """
# -> source.user_portfolio_analysis(0x1234)

""" Get token information"""
# source.token_data(0x123)

"""Fetch all mantle protocol """
# source.fetch_protocol_data()

""" fetch all yield protocol and thier yield"""
# source.fetch_mantle_yield_protocols()

""" Fetch MNT Balance of and account"""
# source.get_balance(0x1234)

""" fetch acoount Token Balance"""
# source.get_token_balance(token_address,wallet_address)