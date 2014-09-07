import datetime

from django.test import TestCase

from studies.models import IndexProduct, \
    Underwriter
from studies.utils import black_scholes_model, \
    implied_volatility

class AssertStructuredProductModels(TestCase):
    def setUp(self):
        underwriter = Underwriter.objects.create(name="XYZ Investment Bank")
        IndexProduct.objects.create(
            name="Stock Index return Security", 
            symbol="SIS", 
            issue_price=10,
            max_price=25,
            issued_at=datetime.date(2014,9,30),
            maturity_at=datetime.date(2015,9,30),
            participation_rate=1,
            adjustment_factor=91.25,
            annual_interest=1,
            volility_estimate=.5,
            underlying_name="S&P Midcap 400 index",
            underlying_symbol="MID",
            underlying_strike_price=166.1,
            underwriter=underwriter         
            )

    def test_underwriter_model_types(self):
        underwriter = Underwriter.objects.first()
        self.assertEqual(
            underwriter._meta.get_field("name").get_internal_type(), 
            "CharField")

    def test_indexproduct_model_types(self):
        indexproduct = IndexProduct.objects.first()
        self.assertEqual(
            indexproduct._meta.get_field("name").get_internal_type(),
            "CharField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("symbol").get_internal_type(),
            "CharField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("issue_price").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("max_price").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("issued_at").get_internal_type(),
            "DateField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("maturity_at").get_internal_type(),
            "DateField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("participation_rate").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("adjustment_factor").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("annual_interest").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("volility_estimate").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("underlying_name").get_internal_type(),
            "CharField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("underlying_symbol").get_internal_type(),
            "CharField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("underlying_strike_price").get_internal_type(),
            "FloatField"
            )
        self.assertEqual(
            indexproduct._meta.get_field("underwriter").get_internal_type(),
            "ForeignKey"
            )
        indexproduct.max_price = None
        indexproduct.save()
        assert(not indexproduct.max_price)
        indexproduct.adjustment_factor = None
        indexproduct.save()
        assert(not indexproduct.adjustment_factor)
        indexproduct.participation_rate = None
        indexproduct.save()
        assert(not indexproduct.adjustment_factor)


class AssertIndexProductModelMethods(TestCase):
    def setUp(self):
        underwriter = Underwriter.objects.create(name="XYZ Investment Bank")
        IndexProduct.objects.create(
            name="Stock Index return Security", 
            symbol="SIS", 
            issue_price=10,
            issued_at=datetime.date(1993,6,2),
            maturity_at=datetime.date(2000,6,2),
            participation_rate=1.15,
            annual_interest=.055,
            volility_estimate=.5,
            underlying_name="S&P Midcap 400 index",
            underlying_symbol="MID",
            underlying_strike_price=166.1,
            underwriter=underwriter         
            )

    def test_duration_in_days(self):
        indexproduct = IndexProduct.objects.first()
        self.assertEqual(indexproduct.duration_in_days(), 2557)

    def test_duration_in_years(self):
        indexproduct = IndexProduct.objects.first()
        self.assertEqual(indexproduct.duration_in_years(), 7)

    def test_cash_surrender_value(self):
        indexproduct = IndexProduct.objects.first()
        # generic example pg 597
        self.assertEqual(indexproduct.cash_surrender_value(233.98), 14.7)
        # bull spread example pg 608
        indexproduct.max_price = 25
        indexproduct.underlying_strike_price = 150
        indexproduct.save()
        self.assertEqual(indexproduct.cash_surrender_value(210), None)
        indexproduct.participation_rate = None
        indexproduct.issued_at = datetime.date(1995,6,2)
        indexproduct.annual_interest = 0
        indexproduct.save()
        self.assertNotEqual(indexproduct.cash_surrender_value(210), 13.60)
        self.assertEqual(round(indexproduct.cash_surrender_value(210),1), 13.60)
        # adjustment example: pg 603
        indexproduct.adjustment_factor = .0875
        indexproduct.save()
        self.assertEqual(indexproduct.cash_surrender_value(210), None)
        indexproduct.max_price = None
        indexproduct.underlying_strike_price = 1100
        indexproduct.save()
        self.assertEqual(indexproduct.cash_surrender_value(2200), 18.25)

    def test_money_in_the_bank(self):
        indexproduct = IndexProduct.objects.first()
        #pg 597
        self.assertEqual(indexproduct.money_in_the_bank(), 14.7)

    def test_embedded_call_price(self):
        indexproduct = IndexProduct.objects.first()
        # pg 597
        self.assertEqual(indexproduct.embedded_call_price(), 4.087)

    def test_implied_volatility_of_embedded_call(self):
        indexproduct = IndexProduct.objects.first()
        # pg 597
        self.assertEqual(indexproduct.implied_volatility_of_embedded_call(), 
            .25)

    def test_cash_val_for_bull_spread(self):
        indexproduct = IndexProduct.objects.first()
        indexproduct.max_price = 25
        indexproduct.underlying_strike_price = 150
        indexproduct.participation_rate = None
        indexproduct.save()
        indexproduct.issued_at = datetime.date(1995,6,2)
        indexproduct.annual_interest = 0
        indexproduct.save()
        self.assertEqual(indexproduct.cash_val_for_bull_spread(210), 14)

    def test_val_of_bull_spread_calls(self):
        indexproduct = IndexProduct.objects.first()
        indexproduct.max_price = 25
        indexproduct.underlying_strike_price = 150
        indexproduct.participation_rate = None
        indexproduct.save()
        indexproduct.issued_at = datetime.date(1995,6,2)
        indexproduct.annual_interest = 0
        indexproduct.save()
        cash_val = indexproduct.cash_val_for_bull_spread(210)
        self.assertNotEqual(indexproduct.val_of_bull_spread_calls(cash_val), 
            (7.3, 3.7))
        call1, call2 = indexproduct.val_of_bull_spread_calls(cash_val)
        self.assertEqual((round(call1, 1), round(call2, 1)), (7.3, 3.7))

    def test_trading_discount(self):
        indexproduct = IndexProduct.objects.first()
        #pg 598
        current_market_price = 13
        current_index_value = 238.54
        self.assertEqual(indexproduct.trading_discount(current_market_price,
            current_index_value), 2.02)

    def test_trading_discount_as_percent_of_current_market_price(self):
        indexproduct = IndexProduct.objects.first()
        #pg 599
        current_market_price = 13
        current_index_value = 238.54
        self.assertEqual(
            indexproduct.trading_discount_as_percent_of_current_market_price(
                current_market_price,
                current_index_value), .16)

    def test_trading_discount_as_downside_protection(self):
        # pg 600
        indexproduct = IndexProduct.objects.first()
        current_market_price = 13
        current_index_value = 238.54
        self.assertEqual(
            indexproduct.trading_discount_as_downside_protection(
                current_market_price,
                current_index_value), .12)

    def test_break_even_final_index_value(self):
        # pg 604
        indexproduct = IndexProduct.objects.first()
        self.assertEqual(
            indexproduct.break_even_final_index_value(), 
            indexproduct.underlying_strike_price)
        indexproduct.adjustment_factor = .0875
        indexproduct.underlying_strike_price = 1100
        indexproduct.save()
        self.assertEqual(indexproduct.break_even_final_index_value(), 
            1205.48)

    def test_max_price_in_terms_of_index_value(self):
        # pg 610
        indexproduct = IndexProduct.objects.first()
        indexproduct.max_price = 25
        indexproduct.underlying_strike_price = 150
        indexproduct.issued_at = datetime.date(1995,6,2)
        indexproduct.annual_interest = 0
        indexproduct.save()
        self.assertEqual(
            indexproduct.max_price_in_terms_of_index_value(), 
            375
            )

    def test_multiplier(self):
        # pg 614
        indexproduct = IndexProduct.objects.first()
        indexproduct.underlying_strike_price = 700
        indexproduct.save()
        self.assertEqual(
            indexproduct.multiplier(), 
            70
            )

    def test_index_equivalent_shares(self):
        indexproduct = IndexProduct.objects.first()
        # pg 614
        indexproduct = IndexProduct.objects.first()
        indexproduct.underlying_strike_price = 700
        indexproduct.save()
        self.assertEqual(
            indexproduct.index_equivalent_shares(15000), 
            214.29
            )

    def test_number_of_calls_to_write(self):
        indexproduct = IndexProduct.objects.first()
        # pg 614
        indexproduct = IndexProduct.objects.first()
        indexproduct.underlying_strike_price = 700
        indexproduct.save()
        self.assertEqual(
            indexproduct.number_of_calls_to_write(15000), 
            2
            )

class AssertUtils(TestCase):

    def test_black_scholes_model(self):
        self.assertEqual(
            black_scholes_model(60, 45, 50, .3, .1),
            .7746
            )

    def test_implied_volatility(self):
        v_starter = float(.001)
        incr = float(.0001)
        self.assertEqual(
            round(implied_volatility(60,45,50,v_starter,.1, .7746,incr),2),
            .3)