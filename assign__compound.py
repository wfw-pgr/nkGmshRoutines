import os, sys, re
import numpy         as np
# import gmsh_api.gmsh as gmsh
import gmsh

# ========================================================= #
# ===  assign compound entities                         === #
# ========================================================= #
def assign__compound( meshFile=None, physFile=None, target="volu" ):

