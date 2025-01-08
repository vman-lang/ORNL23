#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 07 2023
@author: Srikanth Yoginath

"""
import sys
import numpy as np
import pydantic
from pydantic import BaseModel
from typing import List
import json


class StaticConfig(BaseModel):
    name: str

class Complex(BaseModel):
    real: float
    imag: float

def np_to_complex_list_of_lists(array):
    return [
        [Complex(real=element.real, imag=element.imag) for element in row]
        for row in array
    ]


def np_matrix_to_list_of_lists(array):
    return [
        [element for element in row]
        for row in array
    ]


def list_of_lists_to_np_mat(mat):
    np_mat = np.array([np.array(i) for i in mat], dtype=object)
    return np_mat


def list_of_lists_to_complex_np_mat (mat):
    np_mat = np.array([[x.real + 1j * x.imag for x in row] for row in mat])
    # np_mat = np.array([np.array(i.real +1j*i.imag) for i in mat], dtype=object)
    return np_mat


def list_of_lists_of_tuples_to_complex_np_mat (mat):
    np_mat = np.array([[x[0] + 1j * x[1] for x in row] for row in mat])
    return np_mat


################################################################################
class LoLF(BaseModel):
    vals: List[List[float]] = None # list(list(float))

def update_LoLF(xn):
    ret_LoLF = LoLF()
    ret_LoLF.vals = xn
    return ret_LoLF

def LoLF_to_send(xn):
    ret_lolf = LoLF()
    ret_lolf.vals = np_matrix_to_list_of_lists(xn)  # list(list(float))
    return ret_lolf

def LoLF_after_recv(xn):
    ret_lolf = LoLF()
    ret_lolf.vals = list_of_lists_to_np_mat (xn.vals)  # list(list(float))
    return ret_lolf.vals

################################################################################
class ListS(BaseModel):
    vals: List[str] = None # list(str)

def update_ListS(xn):
    ret_listS = ListS()
    ret_listS.vals = xn
    return ret_listS

def ListS_to_send(xn):
    ret_listS = ListS()
    ret_listS.vals = xn  # list(str)
    return ret_listS

def ListS_after_recv(xn):
    ret_listS = ListS()
    ret_listS.vals = xn.vals  # list(str)
    return ret_listS.vals

################################################################################
class ListF(BaseModel):
    vals: List[float] = None # list(float)

def update_ListF(xn):
    ret_ListF = ListF()
    ret_ListF.vals = xn
    return ret_ListF

def ListF_to_send(xn):
    ret_listf = ListF()
    ret_listf.vals =  xn #xn.tolist()  # list(float)
    return ret_listf

def ListF_after_recv(xn):
    ret_listf = ListF()
    ret_listf.vals =  xn.vals # np.array(xn.vals)  # np.array(float)
    return ret_listf.vals

################################################################################
