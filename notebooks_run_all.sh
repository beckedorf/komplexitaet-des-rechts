#!/bin/sh

jupyter nbconvert \
--ExecutePreprocessor.timeout=-1 \
--execute \
--to notebook \
--inplace $(find notebooks/*.ipynb | xargs echo)
