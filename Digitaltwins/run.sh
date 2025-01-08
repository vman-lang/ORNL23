#!/bin/bash

ps -eaf | grep miniconda3 | awk '{ print $2}'  | xargs kill -9
python test_full_systems.py
helics run --path=build/test_system_runner.json
