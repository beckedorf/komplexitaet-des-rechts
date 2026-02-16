#!/bin/sh

jupyter nbconvert \
--ClearOutputPreprocessor.enabled=True \
--clear-output \
--to notebook \
--inplace $(find notebooks/*.ipynb | xargs echo)
