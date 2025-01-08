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
import tensorflow as tf

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

abs_path = os.path.abspath("../..")
utils_path = abs_path + "/utils"
print("utils_path:", utils_path)
sys.path.insert(1, utils_path)
from data_structures import ListF, ListF_to_send, ListF_after_recv

class DigitalTwinConfig(BaseModel):
    name: str
    in_file: str


class DigitalTwin:
    def __init__(self, config: DigitalTwinConfig, input_mapping):
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
        self.in_file = config.in_file

        self.vfed = h.helicsCreateValueFederate(config.name, fedinfo)
        print("Value federate created")

        # Register subscription
        self.sub_field_vals = self.vfed.register_subscription(
            input_mapping["field_vals"], ""
        )
        # Register publication #
        self.pub_pred_vals = self.vfed.register_publication(
             "pred_vals", h.HELICS_DATA_TYPE_STRING, ""
        )

        self.loaded_model = self.load_model() 


    def load_model(self):
        json_file = open("cos2_model.json", 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = tf.keras.models.model_from_json(loaded_model_json)
        loaded_model.load_weights("my_cos2_model.h5")
        return loaded_model


    def get_pred_values (self, field_vals):
        model_input = np.array(field_vals)
        model_input = model_input.reshape(50,1)
        pred_val = self.loaded_model.predict(model_input)
        print ("*pred_val: " , pred_val[0])
        pred_val_list = pred_val.flatten().tolist()

        #num_vals = 3
        #pred_val_list = []
        #for i in range(0,num_vals):
        #    pred_val_list.append(random.random())
        return pred_val_list


    def run(self):
        # Enter execution mode #
        self.vfed.enter_executing_mode()
        print("Entering execution mode")

        granted_time = h.helicsFederateRequestTime(self.vfed, h.HELICS_TIME_MAXTIME)
        prev_pred_vals = [0.0, 0.0]
        while granted_time < h.HELICS_TIME_MAXTIME:
            if (granted_time >= 5.0):
                print("granted_time:", granted_time)
                field_vals_rcvd = ListF.parse_obj(self.sub_field_vals.json)
                field_vals = ListF_after_recv(field_vals_rcvd)
                print ("field_vals : ", field_vals)

                pred_vals_send = ListF_to_send(prev_pred_vals)
                print ("pred_vals_send : ", pred_vals_send)
                print ("pred_vals_send.json : ", pred_vals_send.json())
                self.pub_pred_vals.publish(pred_vals_send.json())

                pred_vals  = self.get_pred_values(field_vals)
                print ("pred_vals : ", pred_vals)
                prev_pred_vals = pred_vals

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
        config = DigitalTwinConfig(**json.load(f))

    with open("input_mapping.json") as f:
        input_mapping = json.load(f)

    sfed = DigitalTwin(config, input_mapping)
    sfed.run()
    END = time.perf_counter() - START
    mem = (psutil.Process().memory_info().vms / (1024 ** 2))
    print("Runtime(seconds) Memory(MiB)")
    print(f"{END:0.2f}", f"{mem:0.2f}")
    print("--DONE--")
