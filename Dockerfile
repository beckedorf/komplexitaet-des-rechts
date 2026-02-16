FROM ubuntu:20.04

# set up packages
RUN apt-get update -qq
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y \
    texlive \
    lyx \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-lang-german \
    imagemagick \
    aspell-de \
    hunspell-de-de \
    texlive-font-utils \
    git \
    texlive-bibtex-extra biber \
    latexmk \
    texlive-luatex \
    language-pack-de \
    language-pack-de-base \
    chromium-chromedriver \
    curl \
    python3-pip \
    texlive-extra-utils \
    && \
    apt-get install -y libxml2-dev libxslt-dev

WORKDIR /root

COPY requirements.txt /root/requirements.txt
RUN pip install $(grep -i "cmake" /root/requirements.txt) && \
    pip install -r /root/requirements.txt

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections
RUN apt-get --reinstall -y --no-install-recommends install ttf-mscorefonts-installer

RUN curl -fsSL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    rm nodesource_setup.sh && \
    apt-get install -y nodejs && \
    npm install vega@5.20.0 vega-cli@5.20.0 vega-lite@5.0.0

RUN git clone --depth=1 https://github.com/QuantLaw/legal-data-clustering.git