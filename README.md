# KZG-Attack
Attack on KZG when toxic waste is not discarded

## Prerequisites

This script requires Python 3.x and the Ethereum `py_ecc` library to perform operations on the BN128 elliptic curve.


## Installation

Install the required cryptographic dependency using pip inside a python virtual environment:

    $ python3 -m venv virtualenv
    $ source virtualenv/bin/activate
    $ pip3 install py_ecc

## To repoduce the attack go into PART1 directory: 

    $ python3 attack.py

A random fake value for polynomial (**poly(z)**) is being used in the script. It can be replaced with any value (not real one) for demo. 
