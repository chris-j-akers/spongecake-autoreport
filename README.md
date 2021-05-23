# Spongecake Autoreport

- [Introduction](#introduction)
- [Example](#example)
- [Instructions](#instructions)
  - [Pre-requisities](#pre-requisities)
  - [Configuring the Watchlist](#configuring-the-watchlist)
  - [Running Spongecake Autoreport](#running-spongecake-autoreport)
- [Running as a Docker Container](#running-as-a-docker-container)
- [Appendix A - `emailer.py`](#appendix-a---emailerpy)

## Introduction

Spongecake Autoreport will generate a PDF report of Technical Charts (Price/Volume, Stochastic Oscillator and Moving Average Convergence/Divergence) for a list of tradable instrument mnemonics (TIDMS) and provide some extra income and balance sheet data and a few fundamental calculations.

Note that, Spongecake Autoreport and Spongecake Financials have both only been used and tested with London Stock Exchange instruments.

## Example

Below is an example of a chart generated for FDEV (Frontier Developments Plc).

Charts are printed one per page. There is currently no limit to the number of charts that can be generated.

![](readme_img/autoreport-example.png)


## Instructions

### Pre-requisities

Spongecake Autoreport needs the following installed:

* Python 3 & Pip
* Spongecake-Financials ([https://github.com/chris-j-akers/spongecake-financials](https://github.com/chris-j-akers/spongecake-financials))
* Pandas
* pandas_datareader
* requests
* Matplotlib
* Weasyprint

By default, the program uses the `/tmp` directory to output it's reports.

### Configuring the Watchlist

A file called `watchlist` must exist in the directory of the repo and be populated in the format:

`tidm|company name|description`

Note fields are separated by `|` (pipe).

`tidm` is the tradable instrument mnemonic of the company, `company name` is the name of the company and `description` is a brief free-text description of the company and what it does.

e.g.

```
GAW|Games Workshop|Games Workshop Group PLC designs, manufactures and sells fantasy miniatures and related products.
KWS|Keywords Studios|Keywords Studios Plc supplies localization and localization testing services. 
```

Any line beginning `#` will be ignored.

An example file is included in the repo.

### Running Spongecake Autoreport

The program can be run with the following command:

`➜ python ./spongecake_autoreport.py`

Output should be similar to below, with the final line stating the location of the final report.

```
Getting data for TIDM FDEV
Getting data for TIDM GAW
Getting data for TIDM KWS
Getting data for TIDM TM17
Getting data for TIDM EMIS
Getting data for TIDM SCT
Getting data for TIDM SPX
Getting data for TIDM KNOS
Getting data for TIDM D4T4
Getting data for TIDM PAY
Getting data for TIDM IOM
Getting data for TIDM TUNE
Getting data for TIDM ZOO
Getting data for TIDM CCC
Report generated at: /tmp/0a3dd596-baf9-40e4-a60f-df7c96584d56_scautoreport/spongecake_2021_05_21.pdf
```
## Running as a Docker Container

Spongecake Autoreport can be run as a container so you don't have to download and configure all the required libraries on your own host.

At the moment, one limitation is that if you change the 'watchlist' config file you need to rebuild the image. The step which copies the 'watchlist' file over is one of the last steps in the Docker file, though, so it doesn't actually take that long to rebuild. This could obviously be fixed at some point with a volume attached to the repo directory.

The image is also quite large (800MB) as the libraries used have a lot of dependencies and it uses the Canonical Ubuntu image.

To build the Docker image run the following from the repo directory:

`docker image build -t spongecake-autoreport .`

Spongecake-autoreport, by default, outputs reports to the `/tmp` directory. The Dockerfile configures a `/tmp` volume which must be mapped to a directory on the host using the `-v` switch when running the container. If not, the report will be inaccessible.

For instance, to generate the report and store it in the host's own `/tmp` directory, run:

`docker container run -v /tmp:/tmp spongecake-autoreport`

The output will be similar to above, except Docker doesn't flush `stdout` immediately, so it may take a while before the text is fully displayed.

## Appendix A - `emailer.py`

The `emailer.py` module included used to provide automatic emailing of the report once it had been generated, but the call has since been removed from the `main()` function of the application as it isn't secure.

The module should never be used with your current personal or business email addresses as it requires that the 'Less Secure Apps' option to be enabled on you Gmail account.

It has been left as part of the repo, though, for anyone who wants to put it back. 

The `emailer.py` requires two environment variables to be set:

* `GMAIL_USER=gmail.address.to.send.from@gmail.com`
* `GMAIL_PASSWORD=password.to.above.gmail.account`

