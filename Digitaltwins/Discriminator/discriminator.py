import sys, os, time, psutil
import numpy as np
import scipy.sparse as sp
from scipy.io import loadmat

from scipy.sparse import csr_matrix, csc_matrix, lil_matrix, identity
from scipy.sparse.linalg import splu
from scipy.linalg import block_diag
from scipy.sparse.linalg import spsolve
from scipy.linalg import lstsq

import helics as h
import numpy as np
from pydantic import BaseModel
from typing import List
import scipy.io
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

from data_structures import ListF, ListF_after_recv

class DiscriminatorConfig(BaseModel):
    name: str
    in_file: str


class Discriminator:
    def __init__(self, config: DiscriminatorConfig, input_mapping):
        # self.rng = np.random.default_rng(12345)
        deltat = 0.05

        # Create Federate Info object that describes the federate properties #
        fedinfo = h.helicsCreateFederateInfo()
        fedinfo.core_name = config.name
        fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
        fedinfo.core_init = "--federates=1"
        print(config.name)

        h.helicsFederateInfoSetTimeProperty(
            fedinfo, h.helics_property_time_delta, deltat
        )

        self.vfed = h.helicsCreateValueFederate(config.name, fedinfo)
        print("Value federate created")

        # Register subscription
        self.sub_field_vals = self.vfed.register_subscription(
            input_mapping["field_vals"], ""
        )
        self.sub_pred_vals = self.vfed.register_subscription(
            input_mapping["pred_vals"], ""
        )

        # Register publication #
        #self.pub_diff_vals = self.vfed.register_publication(
        #     "diff_vals", h.HELICS_DATA_TYPE_STRING, ""
        #)


    def get_diff_values (self, fvals, pvals):
        field_val  = fvals[-1]
        pred_val = pvals[0]

        diff = abs(field_val - pred_val)

        #diff_list = []
        #for i in range(0, len(fvals)):
        #    diff_list.append(fvals[i] - pvals[i])

        return diff


    def run(self):
        # Enter execution mode #
        self.vfed.enter_executing_mode()
        print("Entering execution mode")

        granted_time = h.helicsFederateRequestTime(self.vfed, h.HELICS_TIME_MAXTIME)

        while granted_time < h.HELICS_TIME_MAXTIME:
            if (granted_time >= 5.1):
                print("granted_time:", granted_time)

                field_vals_rcvd = ListF.parse_obj(self.sub_field_vals.json)
                field_vals = ListF_after_recv(field_vals_rcvd)
                print ("field_vals : ", field_vals)
            
                
                print ("pred_vals_json : ", self.sub_pred_vals.json)
                pred_vals_rcvd = ListF.parse_obj(self.sub_pred_vals.json)
                pred_vals = ListF_after_recv(pred_vals_rcvd)
                print ("pred_vals : ", pred_vals)

                diff_vals  = self.get_diff_values(field_vals, pred_vals)
                print ("granted_time:" , granted_time , " Diff: ", diff_vals)

                #diff_vals_send = ListF_to_send(diff_vals)
                #self.pub_diff_vals.publish(diff_vals_send.json())

            granted_time = h.helicsFederateRequestTime(self.vfed, h.HELICS_TIME_MAXTIME)
        self.destroy()


    def destroy(self):
        h.helicsFederateDisconnect(self.vfed)
        print("Federate disconnected")
        h.helicsFederateFree(self.vfed)
        h.helicsCloseLibrary()


if __name__ == "__main__":
    START = time.perf_counter()
    with open("static_inputs.json") as f:
        config = DiscriminatorConfig (**json.load(f))

    with open("input_mapping.json") as f:
        input_mapping = json.load(f)

    sfed = Discriminator(config, input_mapping)
    sfed.run()
    END = time.perf_counter() - START
    mem = (psutil.Process().memory_info().vms / (1024 ** 2))
    print("Runtime(seconds) Memory(MiB)")
    print(f"{END:0.2f}", f"{mem:0.2f}")
    print("--DONE--")

