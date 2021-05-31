# Dockerfile to generate a Spongecake-Autoreport image
# Note that this generates a fairly large image of around 800MB
#
# From Ubuntu (Minimal should be the default)
#
# Could change this to a more minimal Linux distro at some point, but everything
# here has been tested on Ubunut

FROM ubuntu

# Have to set timezone because some of the Cairo library installers appear to
# check it and, if it's not set, stops the whole process to prompt you for
# it

ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Python & Pip

RUN apt-get update \
&& apt-get install -y python3 \
&& apt-get install -y python3-pip

# Install Git so we can clone the repos

RUN apt-get install -y git

# Python packages used by Spongecake Autoreport

RUN pip install pandas \
&& pip install matplotlib \
&& pip install weasyprint \
&& pip install requests \
&& pip install pandas_datareader

# Libs required by WeasyPrint

RUN apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

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

# Copy the local version of the 'watchlist' configuration file over
COPY ./watchlist /usr/src/spongecake/spongecake-autoreport/

# Finally run the report
WORKDIR /usr/src/spongecake/spongecake-autoreport/
CMD ["python3","spongecake_autoreport.py"]

# All reports are written to /tmp by default. If this is changed in the code,
# then the volume will need to be changed here, too.
VOLUME /tmp
