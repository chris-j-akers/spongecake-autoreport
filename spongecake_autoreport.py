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
from company import Company



def get_technicals_chart_for_instrument(df_prices, 
                                        instrument_description, 
                                        figsize=(25,6),
                                        linewidth=3):
    '''
    Produce 3-chart matplotlib figure from a list of dates and prices for a
    particular instrument.

    Parameters: 

        df_prices: A dataframe consisting of dates and prices for a particular instrument
        instrument_descrription: Plain text description of the instrument
        figsize: Size of the final figure to be returned
        linewidth: Line width to use for the charts

    Returns:

        A Matplotlib figure consisting of 3 charts (from top to bottom):

            * Closing Period Price and Volume Chart
            * Stochastic Oscillator Chart
            * MACD Chart

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

    '''
    Spongecake-Autoreport is built around Yahoo prices which are free, but
    aren't perfect. Occasionally there will be anomalies and these will need to
    be fixed or smoothed over until Yahoo themselves get around to it.

    This function is called when generating the report and logic can be added
    to adjust prices where necessary.

    If this function is empty, then that means prices are all good!

    Parameters:

        tidm: The tidm (mnemonic) of the affected instrument
        df_prices: A Dataframe of dates and prices for the affected instrument

    Returns:

        An adjusted Dataframe with smoothed over or corrected prices
    '''

    # If there's no code, here, then that's good!

    return df_prices

def build_calcs_table(tidm):
    '''
    Uses the InvestorsChronicleInterface of Spongecake-Financials to build a
    Dataframe of fundamental calculations that can be printed out on each sheet
    along with the charts and other fundamental data.

    Calculations added are:

        * CURRENT RATIO
        * ROCE (return on capital employed)
        * EARNINGS YIELD % (TTM)
        * NAV (£m)
        * NAV PER SHARE (£)
        * NAV PER SHARE AS % OF PRICE

    Parameters:

        tidm: The tidm (mnemonic) of the instrument

    Returns:

        A new Dataframe with the above fundamental calculations

    '''
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
    Create a temporary directory using a new UUID.

    The directory name takes the format: {GUID}_scautoreport

    Parameters:

        tmp_location: The location to create the temporary directory (default = /tmp)
        
    Returns:

        The full path of the new directory
    '''
    dir_uuid = uuid.uuid4()
    path = '{0}/{1}_scautoreport'.format(tmp_location, dir_uuid)
    os.mkdir(path)
    return path
    

def get_watchlist():
    '''
    Collect and return a list of Spongecake Financials Company objects (TIDMs,
    Descrptions and Company Names) based on the watchlist configuration file.

    Returns:

        A list of Spongecake Financials Company objects
    '''
    watchlist = {}
    watchlist_file = open('watchlist','r')
    lines = watchlist_file.readlines()
    for line in lines:
        if line[0] != '#':
            tidm,name,description = line.split('|')
            tidm = tidm.rstrip().lstrip()
            name = name.rstrip().lstrip()
            description = description.rstrip().lstrip()
            watchlist[tidm] = Company(tidm, name, description)
    return watchlist

def generate_pdf_report(watchlist):
    '''
    Generate the report in PDF format. The report consists of Technical Charts,
    Income, Balance and Summary sheets using the Spongecake-Financials package.

    Parameters:

        watchlist: A list of Spongecake-Financials Company objects

    Returns:

        Full path and filename of the PDF report
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
            chart = get_technicals_chart_for_instrument(df_prices, '{0} ({1})'.format(watchlist[tidm].tidm, watchlist[tidm].name))
            fig_filename = '{0}_{1}.png'.format(tidm, date_str)
            chart.savefig('{0}/{1}'.format(tmp_path, fig_filename))
            html += pdf_gen.generate_html('{0} - {1} ({2})'.format(tidm,watchlist[tidm].name, ic.get_current_ic_price(tidm)), watchlist[tidm].description, 'file:///{0}/{1}'.format(tmp_path, fig_filename), income, balance, summary, calcs)
    
    # Send HTML to Weasyprint PDF generator
    report_full_path = '{0}/spongecake_{1}'.format(tmp_path, date_str)
    pdf_gen.generate_pdf(report_full_path, html)

    # Let caller know where it is
    return report_full_path + '.pdf'
    
def main():
    '''
    Entry point. Generate the report and print out it's location.
    '''
    # Have to do this, now, for Matplotlib charts or there will be a deprecation
    # warning
    register_matplotlib_converters()


    report_path = generate_pdf_report(get_watchlist())
    print("Report generated at: {0}".format(report_path))


if __name__ == '__main__':
    main()