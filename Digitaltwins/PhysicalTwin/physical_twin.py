#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, time, psutil
import helics as h
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np 
import json
import random
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

abs_path = os.path.abspath("../..")
utils_path = abs_path + "/utils"
print("utils_path:", utils_path)
sys.path.insert(1, utils_path)

from data_structures import ListF_to_send

class PhysicalTwinConfig(BaseModel):
    name: str
    in_file: str
    number_of_timesteps: str


class PhysicalTwin:
    def __init__(self, config: PhysicalTwinConfig, input_mapping):
        self.deltat = 0.1

        # Create Federate Info object that describes the federate properties #
        fedinfo = h.helicsCreateFederateInfo()
        fedinfo.core_name = config.name
        fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
        fedinfo.core_init = "--federates=1"
        print(config.name)
        h.helicsFederateInfoSetTimeProperty(
            fedinfo, h.helics_property_time_delta, self.deltat
        )
        self.in_file = config.in_file
        self.vfed = h.helicsCreateValueFederate(config.name, fedinfo)
        self.pub_field_vals = h.helicsFederateRegisterPublication(self.vfed, "field_vals", h.HELICS_DATA_TYPE_STRING, "")


    def get_field_values (self, time, prev_field_list):
        
        #update this area to take in more complex/real data

        val = np.cos(time)
        field_val_list = prev_field_list
        field_val_list.append(val)
        len_fl = len(field_val_list)

        if (len_fl > 50):
            n = len_fl - 50
            field_val_list = field_val_list[n:]

        #num_vals = 3
        #field_val_list = []
        #for i in range(0,num_vals):
        #    field_val_list.append(random.random())

        return field_val_list


    def run(self):
        # Enter execution mode #
        self.vfed.enter_executing_mode()
        print("Entering execution mode")
        granted_time = 0 
        start = True
        request_time = 0
        prev_field_list = []
        resolution = 0.1
        
        for i in range(0,50):
            t_time = i * resolution
            print ("requested_time: ", t_time)
            prev_field_list = self.get_field_values(t_time, prev_field_list)

        print ("prev_field_list: ", prev_field_list)
        field_vals_list  = prev_field_list

        for request_time in np.arange(5.0, int(config.number_of_timesteps), 0.1):
            if (granted_time <= request_time):
                print ("request_time:", request_time)
                print ("granted_time: ", granted_time)
                
                field_vals_list = self.get_field_values(request_time, field_vals_list)
                print ("field_vals_list: ", field_vals_list)

                json_field_vals_list = ListF_to_send(field_vals_list)

                self.pub_field_vals.publish(json_field_vals_list.json())

                # request_time += self.deltat
                #request_time = h.HELICS_TIME_MAXTIME

                granted_time = h.helicsFederateRequestTime(self.vfed, request_time)
                print ("* request_time:", request_time)
                print ("* granted_time: ", granted_time)

        self.destroy()


    def destroy(self):
        h.helicsFederateDisconnect(self.vfed)
        print("Federate disconnected")
        h.helicsFederateFree(self.vfed)
        h.helicsCloseLibrary()


if __name__ == "__main__":
    START = time.perf_counter()
    with open("static_inputs.json") as f:
        config = PhysicalTwinConfig(**json.load(f))

    with open("input_mapping.json") as f:
        input_mapping = json.load(f)

    print ("config: ", config)
    sfed = PhysicalTwin(config, input_mapping)
    sfed.run()

    END = time.perf_counter() - START
    mem = (psutil.Process().memory_info().vms / (1024 ** 2))
    print("Runtime(seconds) Memory(MiB)")
    print(f"{END:0.2f}", f"{mem:0.2f}")
    print("--DONE--")

