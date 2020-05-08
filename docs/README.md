Auto-generate and send an email of selected technical charts and fundamental data for watchlist of UK equities.

Uses Gmail to send

Currently uses Yahoo prices to calculate Technicals and screen-scrapes financial websites (Investors Chronicle) to pull Fundamentals.

Technical charts include:

* Close (line) & Volume (bar)
* Stochastic Oscillator
* Moving Average Convergence Divergence

Selected fundamentals are:

* Current Price
* Shares Outstanding
* Market Cap
* Date of Last Balance Sheet
* Date of Last Income Sheet
* Total Revenue
* Net Income After Tax
* Current Ratio
* Total Debt
* NAV Per Share as % of Price
* EPS
* EPS (TTM)
* P/E Ratio
* P/E/Ratio (TTM)
* Earnings Yield %
* Earnings Yield % (TTM)
* Return on Capital Employed (ROCE)

NOTE: Percentages are returned as decimals (e.g. 20% = 0.2)

![Example email](https://github.com/InPursuitOfHisOwnHat/spongecake-autoreport/blob/master/docs/mail.png)

Python libraries required:

* spongecake-financials (https://github.com/InPursuitOfHisOwnHat/spongecake-financials)
* matplotlib
* pandas
* pandas_datareader

Requires a comma-separated file of TIDMs and Company names called 'watchlist' in the app's root directory, e.g:

~~~~
# TIDM,Name
CDM,Codemasters
FDEV,Frontier Developments
KWS,Keywords Studios
~~~~

Requires following environment variables to send the mails:

~~~~
GMAIL_USER=gmail.address.to.send.from@gmail.com
GMAIL_PASSWORD=password.to.above.gmail.account
~~~~






