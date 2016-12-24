#!/usr/bin/env bash
./wait-for-it.sh -t 0 tsdb:4242 -- python ./sampler.py
