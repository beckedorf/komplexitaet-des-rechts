#!/bin/sh
docker build . -t komplexitaet-des-rechts
docker run \
    -v .:/root/komplexitaet-des-rechts/ \
    -v ./../legal-networks-data:/root/legal-networks-data/ \
    -v ./../legal-data-clustering:/root/legal-data-clustering/ \
    -p 8888:8888 \
    -w /root/komplexitaet-des-rechts/ \
    komplexitaet-des-rechts \
    jupyter lab --allow-root --ip=0.0.0.0