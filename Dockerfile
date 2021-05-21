

# Ubuntu (Minimal should be the default)
FROM ubuntu

# Install Python & Pip
RUN apt-get update \
&& apt-get install -y python3 \
&& apt-get install -y python3-pip

# Python packages used by Spongecake Autoreport
RUN pip install pandas \
&& pip install matplotlib \
&& pip install weasyprint

# Just drop in root
WORKDIR /root

# Clone the spongecake-financials repo
git clone -b 

