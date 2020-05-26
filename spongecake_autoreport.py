from datetime import datetime as dt, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters	
import uuid
import os
# My stuff
from spongecake.fundamentals import InvestorsChronicleInterface, IC_INCOME_DATA
from spongecake.technicals import Indicators
from spongecake.prices import YahooPricesInterface
from data_columns import FundamentalsDataColumns, TechnicalsDataColumns
from spongecake_pdf_generator import spongecake_pdf_generator
import html_formatting
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


def get_technical_data_for_instrument(tidm, market='L', number_of_days=180):
    '''
    Download prices data from yahoo and set the MACD/Stochastic Oscillator.
    
    Chops data off at 180 days (~6 months by default)
    '''
    ypi = YahooPricesInterface()
    prices_df = ypi.get_yahoo_prices('tidm.{0}'.format(market))
    Indicators.set_macd(prices_df)
    Indicators.set_stochastic_oscillator(prices_df)
    cut_off_date = dt.today() - timedelta(days=180)
    prices_df = prices_df[prices_df.index > cut_off_date.strftime("%Y-%m-%d")]
    return prices_df


def get_fundamental_data_for_instrument(tidm, market='LSE'):
    '''
    Download some fundamentals (screen-scrape Investors Chronicle)
    '''
    ic = InvestorsChronicleInterface()
    data = {}
    data[FundamentalsDataColumns.COL_CURRENT_PRICE] = ic.get_current_ic_price(tidm)
    data[FundamentalsDataColumns.COL_SHARES_OUTSTANDING] = ic.get_shares_outstanding(tidm)
    data[FundamentalsDataColumns.COL_MARKET_CAP] = ic.get_market_cap(tidm)
    data[FundamentalsDataColumns.COL_DATE_OF_LAST_BALANCE_SHEET] = ic.get_date_of_latest_balance_sheet(tidm)
    data[FundamentalsDataColumns.COL_DATE_OF_LATEST_INCOME_SHEET] = ic.get_date_of_latest_income_sheet(tidm)
    data[FundamentalsDataColumns.COL_TOTAL_REVENUE] = float(max(ic.get_ic_income_sheet(tidm).loc[IC_INCOME_DATA.ROW_TOTAL_REVENUE]))
    data[FundamentalsDataColumns.COL_NET_INCOME_AFTER_TAX] = float(max(ic.get_ic_income_sheet(tidm).loc[IC_INCOME_DATA.ROW_NET_INCOME_AFTER_TAXES]))
    data[FundamentalsDataColumns.COL_CURRENT_RATIO] = ic.get_current_ratio(tidm)
    data[FundamentalsDataColumns.COL_TOTAL_DEBT] = ic.get_total_debt(tidm)
    data[FundamentalsDataColumns.COL_NAV_PER_SHARE_PCT_OF_PRICE] = ic.get_nav_per_share_as_pct_of_price(tidm)
    data[FundamentalsDataColumns.COL_EPS] = ic.get_eps(tidm)
    data[FundamentalsDataColumns.COL_EPS_TTM] = ic.get_eps_ttm(tidm)
    data[FundamentalsDataColumns.COL_PE_RATIO] = ic.get_price_to_earnings_ratio(tidm)
    data[FundamentalsDataColumns.COL_PE_RATIO_TTM] = ic.get_price_to_earnings_ratio_ttm(tidm)
    data[FundamentalsDataColumns.COL_EARNINGS_YIELD_PERCENT] = ic.get_earnings_yield_pct(tidm)
    data[FundamentalsDataColumns.COL_EARNINGS_YIELD_PERCENT_TTM] = ic.get_earnings_yield_pct_ttm(tidm)
    data[FundamentalsDataColumns.COL_ROCE] = ic.get_roce_pct(tidm)
    return data


def get_new_tmp_directory(tmp_location='/tmp'):
    dir_uuid = uuid.uuid4()
    path = '{0}/{1}_scautoreport'.format(tmp_location, dir_uuid)
    os.mkdir(path)
    return path
    

def get_watchlist():
    watchlist = {}
    watchlist_file = open('watchlist','r')
    lines = watchlist_file.readlines()
    for line in lines:
        if line[0] != '#':
            tidm,company = line.split(',')
            watchlist[tidm.rstrip().lstrip()] = company.rstrip().lstrip()
    return watchlist


def generate_pdf_report(watchlist):
    ypi = YahooPricesInterface()
    ic = InvestorsChronicleInterface()
    tmp_path = get_new_tmp_directory()
    date_str = dt.now().strftime('%Y_%m_%d')
    report_email = emailer.email()
    pdf_gen = spongecake_pdf_generator()
    html = ''
    for tidm in watchlist.keys():
        balance = ic.get_ic_balance_sheet(tidm)
        income = ic.get_ic_income_sheet(tidm)
        summary = ic.get_ic_summary_sheet(tidm)
        df_prices = ypi.get_yahoo_prices('{0}'.format(tidm))
        if len(df_prices) >0:
            Indicators.set_macd(df_prices)
            Indicators.set_stochastic_oscillator(df_prices)
            chart = get_technicals_chart_for_instrument(df_prices, '{0} ({1})'.format(watchlist[tidm], tidm))
            fig_filename = '{0}_{1}.png'.format(tidm, date_str)
            chart.savefig('{0}/{1}'.format(tmp_path, fig_filename))
            html += pdf_gen.generate_html('{0} - {1} ({2})'.format(tidm,watchlist[tidm], ic.get_current_ic_price(tidm)), 'file:///{0}/{1}'.format(tmp_path, fig_filename), income, balance, summary)
    report_full_path = '{0}/spongecake_{1}'.format(tmp_path, date_str)
    pdf_gen.generate_pdf(report_full_path, html)
    return report_full_path
    

def build_email(watchlist):
    ypi = YahooPricesInterface()
    tmp_path = get_new_tmp_directory()
    date_str = dt.now().strftime('%Y_%m_%d')
    report_email = emailer.email()
    mail_html = html_formatting.header()
    for tidm in watchlist.keys():
        mail_html += html_formatting.company_header('{0} ({1})'.format(watchlist[tidm], tidm))
        fundamentals = get_fundamental_data_for_instrument(tidm)
        mail_html += html_formatting.fundamentals(fundamentals)
        df_prices = ypi.get_yahoo_prices('{0}'.format(tidm))
        if len(df_prices) >0:
            Indicators.set_macd(df_prices)
            Indicators.set_stochastic_oscillator(df_prices)
            chart = get_technicals_chart_for_instrument(df_prices, '{0} ({1})'.format(watchlist[tidm], tidm))
            fig_filename = '{0}_{1}.png'.format(tidm, date_str)
            chart.savefig('{0}/{1}'.format(tmp_path, fig_filename))
            report_email.add_image('{0}/{1}'.format(tmp_path, fig_filename), fig_filename)
            mail_html += html_formatting.chart(fig_filename)
            mail_html += html_formatting.company_footer()
    mail_html += html_formatting.footer()
    report_email.add_body(mail_html)
    return report_email


def main():
    register_matplotlib_converters()
    pdf_report = generate_pdf_report(get_watchlist())
    # daily_email = build_email(get_watchlist())
    now_str = dt.now().strftime('%Y-%m-%d')
    #daily_email.send('Technicals Report {0}'.format(now_str), recipients='chris.j.akers@gmail.com')


if __name__ == '__main__':
    main()