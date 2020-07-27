from datetime import datetime as dt, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters	
import pandas as pd
import uuid
import os
# My stuff
from spongecake.fundamentals import InvestorsChronicleInterface
from spongecake.technicals import Indicators
from spongecake.prices import YahooPricesInterface
from data_columns import TechnicalsDataColumns
from spongecake_report_generator import SpongecakeReportGenerator
import emailer


def get_technicals_chart_for_instrument(df_prices, 
                                        instrument_description, 
                                        figsize=(25,6),
                                        linewidth=3):
    '''
    Returns a 3 chart Matplotlib figure of Close & Vol, Stochastic Oscillator and MACD.
    '''
    index_min_date = min(df_prices.index)
    index_max_date = max(df_prices.index)

    fig = plt.figure(figsize=figsize)

    close_axes = fig.add_subplot(311)
    close_axes.set_title('{0} Price / Volume'.format(instrument_description), {'fontweight': 'bold'})
    close_axes.plot(df_prices[[TechnicalsDataColumns.COL_CLOSE]], color='black', linewidth=linewidth)
    volume_axes = close_axes.twinx()
    volume_axes.bar(df_prices.index, df_prices[TechnicalsDataColumns.COL_VOLUME], color='grey')
    plt.ticklabel_format(style='plain', axis='y')

    stochastic_axes = fig.add_subplot(312)
    stochastic_axes.plot(df_prices[[TechnicalsDataColumns.COL_STOCHASTIC_K]], color='blue', linewidth=linewidth)
    stochastic_axes.plot(df_prices[[TechnicalsDataColumns.COL_STOCHASTIC_D]], color='red', linewidth=linewidth)
    stochastic_axes.plot([index_min_date, index_max_date],[80,80], color='grey', linewidth=linewidth, linestyle='--')
    stochastic_axes.plot([index_min_date, index_max_date],[20,20], color='grey', linewidth=linewidth, linestyle='--')
    stochastic_axes.fill_between(df_prices.index, 20, 80, color='pink')
    stochastic_axes.set_title('{0} Stochastic'.format(instrument_description), {'fontweight':'bold'})
    plt.ylim(bottom=0, top=100)

    macd_axes = fig.add_subplot(313)
    macd_axes.set_title('{0} MACD'.format(instrument_description), {'fontweight':'bold'})
    macd_axes.plot(df_prices[[TechnicalsDataColumns.COL_MACD]], color='blue', linewidth=linewidth)
    macd_axes.plot(df_prices[[TechnicalsDataColumns.COL_MACD_SIGNAL]],color='red', linewidth=linewidth)
    macd_axes.bar(df_prices.index, df_prices[TechnicalsDataColumns.COL_MACD] - df_prices[TechnicalsDataColumns.COL_MACD_SIGNAL], color='red', width=0.5)

    plt.tight_layout()
    return fig

def santise_prices(tidm, df_prices):

    # Yahoo isn't perfect (but it's free!) and, occasionally we'll have to 
    # 'manually' modify some of their shit. We take the tidm as a parameter
    # because it may just be some prices that are affected. Or could just pay
    # for a reliable feed at some point.

    #   1. 20 June 2020
    #   Some prices for instruments are clearly put in GBP instead of GBX so have
    #   to * by 100 until we're out of the window (6 months at time of writing)

    df_prices.loc['2020-06-30']['HIGH'] = df_prices.loc['2020-06-30']['HIGH'] * 100
    df_prices.loc['2020-06-30']['LOW'] = df_prices.loc['2020-06-30']['LOW'] * 100
    df_prices.loc['2020-06-30']['OPEN'] = df_prices.loc['2020-06-30']['OPEN'] * 100
    df_prices.loc['2020-06-30']['CLOSE'] = df_prices.loc['2020-06-30']['CLOSE'] * 100
    df_prices.loc['2020-06-30']['ADJ CLOSE'] = df_prices.loc['2020-06-30']['ADJ CLOSE'] * 100

    #   2. 02 July 2020 for some tidms
    if tidm in ['CDM','FDEV', 'KWS', 'TM17', 'EMIS', 'SCT','SPX','KNOS', 'PAY', 'IOM','TUNE','ZOO']:
        df_prices.loc['2020-07-02']['HIGH'] = df_prices.loc['2020-07-02']['HIGH'] * 100
        df_prices.loc['2020-07-02']['LOW'] = df_prices.loc['2020-07-02']['LOW'] * 100
        df_prices.loc['2020-07-02']['OPEN'] = df_prices.loc['2020-07-02']['OPEN'] * 100
        df_prices.loc['2020-07-02']['CLOSE'] = df_prices.loc['2020-07-02']['CLOSE'] * 100
        df_prices.loc['2020-07-02']['ADJ CLOSE'] = df_prices.loc['2020-07-02']['ADJ CLOSE'] * 100
       
    #   3. 29 June 2020
    if tidm in ['KWS','KNOS']:
        df_prices.loc['2020-06-29']['HIGH'] = df_prices.loc['2020-06-29']['HIGH'] * 100
        df_prices.loc['2020-06-29']['LOW'] = df_prices.loc['2020-06-29']['LOW'] * 100
        df_prices.loc['2020-06-29']['OPEN'] = df_prices.loc['2020-06-29']['OPEN'] * 100
        df_prices.loc['2020-06-29']['CLOSE'] = df_prices.loc['2020-06-29']['CLOSE'] * 100
        df_prices.loc['2020-06-29']['ADJ CLOSE'] = df_prices.loc['2020-06-29']['ADJ CLOSE'] * 100

    #   4. 6 July 2020 for Sparx
    if tidm in ['SPX']:
        df_prices.loc['2020-07-06']['HIGH'] = df_prices.loc['2020-07-06']['HIGH'] * 100
        df_prices.loc['2020-07-06']['LOW'] = df_prices.loc['2020-07-06']['LOW'] * 100
        df_prices.loc['2020-07-06']['OPEN'] = df_prices.loc['2020-07-06']['OPEN'] * 100
        df_prices.loc['2020-07-06']['CLOSE'] = df_prices.loc['2020-07-06']['CLOSE'] * 100
        df_prices.loc['2020-07-06']['ADJ CLOSE'] = df_prices.loc['2020-07-06']['ADJ CLOSE'] * 100

    return df_prices

def build_calcs_table(tidm):
    ic = InvestorsChronicleInterface()
    df = pd.DataFrame(columns=['CALC LINE ITEM', 'VALUE'])
    rows = [
            {'CALC LINE ITEM': 'CURRENT RATIO', 'VALUE': ic.get_current_ratio(tidm)},
            {'CALC LINE ITEM': 'ROCE', 'VALUE': ic.get_roce_pct(tidm)},
            {'CALC LINE ITEM': 'EARNINGS YIELD % (TTM)', 'VALUE': ic.get_earnings_yield_pct_ttm(tidm)},
            {'CALC LINE ITEM': 'NAV (£m)', 'VALUE': ic.get_nav(tidm)},
            {'CALC LINE ITEM': 'NAV PER SHARE (£)', 'VALUE': ic.get_nav_per_share(tidm)},
            {'CALC LINE ITEM': 'NAV PER SHARE AS % OF PRICE', 'VALUE': ic.get_nav_per_share_as_pct_of_price(tidm)},           
    ]
    df = df.append(rows, ignore_index=True)
    return df

def get_new_tmp_directory(tmp_location='/tmp'):
    '''
    Create a new temporary directory using a new UUID (default base is /tmp)
    '''
    dir_uuid = uuid.uuid4()
    path = '{0}/{1}_scautoreport'.format(tmp_location, dir_uuid)
    os.mkdir(path)
    return path
    

def get_watchlist():
    '''
    Return list of TIDMs and Company Names from the watchlist configuration file
    '''
    watchlist = {}
    watchlist_file = open('watchlist','r')
    lines = watchlist_file.readlines()
    for line in lines:
        if line[0] != '#':
            tidm,company = line.split(',')
            watchlist[tidm.rstrip().lstrip()] = company.rstrip().lstrip()
    return watchlist

def generate_pdf_report(watchlist):
    '''
    Generate a report that consists of Technical Charts, Income, Balance and Summary sheets using the Spongecake-Financials package
    '''
    # Set-up objects
    ypi = YahooPricesInterface()
    ic = InvestorsChronicleInterface()
    tmp_path = get_new_tmp_directory()
    date_str = dt.now().strftime('%Y_%m_%d')
    pdf_gen = SpongecakeReportGenerator()

    # Build html
    html = ''
    for tidm in watchlist.keys():
        print("Getting data for TIDM {0}".format(tidm))
        balance = ic.get_ic_balance_sheet(tidm)
        income = ic.get_ic_income_sheet(tidm)
        summary = ic.get_ic_summary_sheet(tidm)
        calcs = build_calcs_table(tidm)
        df_prices = ypi.get_yahoo_prices('{0}'.format(tidm))
        if len(df_prices) >0:
            df_prices = santise_prices(tidm, df_prices)
            Indicators.set_macd(df_prices)
            Indicators.set_stochastic_oscillator(df_prices)
            chart = get_technicals_chart_for_instrument(df_prices, '{0} ({1})'.format(watchlist[tidm], tidm))
            fig_filename = '{0}_{1}.png'.format(tidm, date_str)
            chart.savefig('{0}/{1}'.format(tmp_path, fig_filename))
            html += pdf_gen.generate_html('{0} - {1} ({2})'.format(tidm,watchlist[tidm], ic.get_current_ic_price(tidm)), 'file:///{0}/{1}'.format(tmp_path, fig_filename), income, balance, summary, calcs)
    
    # Send HTML to Weasyprint PDF generator
    report_full_path = '{0}/spongecake_{1}'.format(tmp_path, date_str)
    pdf_gen.generate_pdf(report_full_path, html)

    # Let caller know where it is
    return report_full_path + '.pdf'
    

def generate_email(watchlist):
    '''
    Produce email with report attached ready to send
    '''
    report_path = generate_pdf_report(watchlist)
    report_email = emailer.Email()
    report_email.add_attachment(report_path)
    return report_email    

def main():
    # Have to do this, now, for Matplotlib charts or you get a deprecation warning
    register_matplotlib_converters()

    daily_email = generate_email(get_watchlist())
    now_str = dt.now().strftime('%Y-%m-%d')
    daily_email.send('Technicals Report {0}'.format(now_str), recipients='chris.j.akers@gmail.com')

if __name__ == '__main__':
    main()