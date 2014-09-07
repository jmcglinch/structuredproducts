import math

from django.db import models

from studies.utils import implied_volatility, \
    black_scholes_model

class IndexProduct(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)
    issue_price = models.FloatField()
    max_price = models.FloatField(null=True, blank=True)
    issued_at = models.DateField()
    maturity_at = models.DateField()
    participation_rate = models.FloatField(null=True, blank=True)
    adjustment_factor = models.FloatField(null=True, blank=True)
    annual_interest = models.FloatField()
    volility_estimate = models.FloatField()
    underlying_name = models.CharField(max_length=50)
    underlying_symbol = models.CharField(max_length=50)
    underlying_strike_price = models.FloatField()
    underwriter = models.ForeignKey("studies.Underwriter", 
        related_name="index_products") 

    def duration_in_days(self):
        return (self.maturity_at - self.issued_at).days

    def duration_in_years(self):
        return round(self.duration_in_days()/float(365),0)

    def cash_surrender_value(self, final_index_value):
        if type(final_index_value) is not float:
            final_index_value = float(final_index_value)
        if self.adjustment_factor:
            final_index_value = (1-self.adjustment_factor) * final_index_value
        if self.max_price and self.adjustment_factor or \
            self.max_price and self.participation_rate:
            return None
        elif self.max_price:
            cash_val = self.cash_val_for_bull_spread(final_index_value)
            cal_vals = self.val_of_bull_spread_calls(cash_val)
            return round(self.issue_price + cal_vals[0] - cal_vals[1],2)
        else:
            if not self.participation_rate:
                self.participation_rate = 1
                self.save()
            calculated_val = self.issue_price + \
                self.issue_price * self.participation_rate * \
                (final_index_value/self.underlying_strike_price - \
                    1)
            return round(max(self.issue_price, calculated_val),2) 

    def cash_val_for_bull_spread(self, final_index_value):
        if type(final_index_value) is not float:
            final_index_value = float(final_index_value)
        return  self.issue_price * \
            (final_index_value/self.underlying_strike_price)

    def money_in_the_bank(self): 
        return round(self.issue_price * \
            math.exp(self.annual_interest * self.duration_in_years()),2)

    def final_index_mib_val(self):
        money_in_the_bank = self.money_in_the_bank()
        c1 = self.issue_price * self.participation_rate
        final_index_value = (float(money_in_the_bank) \
            - float(self.issue_price) + c1) * \
            float(self.underlying_strike_price)/float(c1)
        return final_index_value

    def embedded_call_price(self):
        final_index_mib_val = self.final_index_mib_val()
        return round(self.issue_price * (final_index_mib_val / \
            self.underlying_strike_price - 1),3)

    def implied_volatility_of_embedded_call(self):
        embedded_call_price = self.embedded_call_price()
        v_starter = float(0.01)
        incr = float(0.0001)
        return round(implied_volatility(self.duration_in_days(), 
            self.issue_price, self.issue_price,
            v_starter, self.annual_interest, embedded_call_price, 
            incr),2)

    def val_of_bull_spread_calls(self, cash_val):
        call1 = black_scholes_model(self.duration_in_days(), 
            cash_val, self.issue_price, self.volility_estimate, 
            self.annual_interest)
        call2 = black_scholes_model(self.duration_in_days(), 
            cash_val, self.max_price, self.volility_estimate, 
            self.annual_interest)
        return (round(call1,2), round(call2,2))

    def trading_discount(self, current_market_price, current_index_value):
        return round(self.cash_surrender_value(current_index_value) - \
            current_market_price,2)

    def trading_discount_as_percent_of_current_market_price(self, 
            current_market_price, current_index_value):
        discount = self.trading_discount(current_market_price,
            current_index_value)
        return round(float(discount)/float(current_market_price),2)

    def trading_discount_as_downside_protection(self, current_market_price, 
            current_index_value):
        c1 = self.issue_price * self.participation_rate
        c2 = (float(current_market_price) \
            - float(self.issue_price) + c1) * \
            float(self.underlying_strike_price)/float(c1)
        return round((current_index_value - c2)/current_index_value,2)

    def break_even_final_index_value(self):
        if self.adjustment_factor:
            return round(self.underlying_strike_price/(float(1)-self.adjustment_factor),2)
        else:
            return self.underlying_strike_price

    def max_price_in_terms_of_index_value(self):
        return (self.max_price/self.issue_price) * self.underlying_strike_price

    def multiplier(self):
        return self.underlying_strike_price/self.issue_price

    def index_equivalent_shares(self, shares_held):
        multiplier = self.multiplier()
        return round(float(shares_held) / multiplier,2)

    def number_of_calls_to_write(self, shares_held):
        index_equivalent_shares = self.index_equivalent_shares(shares_held)
        return round(index_equivalent_shares/100, 0)


class Underwriter(models.Model):
    name = models.CharField(max_length=50)