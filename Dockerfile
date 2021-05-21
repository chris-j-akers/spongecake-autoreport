# Ubuntu (Minimal should be the default)
FROM ubuntu

# Install Python & Pip
RUN apt-get update \
&& apt-get install -y python3 \
&& apt-get install -y python3-pip

RUN apt-get install -y git

# Python packages used by Spongecake Autoreport
RUN pip install pandas \
&& pip install matplotlib \
&& pip install weasyprint

# Create DIR for app files
RUN mkdir /usr/src/spongecake/
WORKDIR /usr/src/spongecake/

# Clone the spongecake-financials repo
RUN git clone https://github.com/chris-j-akers/spongecake-financials.git

# Install the Spongecake Financials package
WORKDIR /usr/src/spongecake/spongecake-financials/
RUN python3 setup.py bdist_wheel
RUN pip install ./dist/spongecake-1.0-py3-none-any.whl

# Clone the spongecake-autoreport repo
WORKDIR /usr/src/spongecake/
RUN git clone https://github.com/chris-j-akers/spongecake-autoreport.git

