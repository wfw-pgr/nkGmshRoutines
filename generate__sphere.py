import numpy as np
import os, sys
import gmsh_api.gmsh as gmsh

# ------------------------------------------------- #
# --- [1] initialization of the gmsh            --- #
# ------------------------------------------------- #
gmsh.initialize()
gmsh.option.setNumber( "General.Terminal", 1 )
gmsh.model.add( "model" )

# ------------------------------------------------- #
# --- [2] initialize settings                   --- #
# ------------------------------------------------- #
ptsDim , lineDim , surfDim , voluDim  =  0,  1,  2,  3
pts    , line    , surf    , volu     = {}, {}, {}, {}
ptsPhys, linePhys, surfPhys, voluPhys = {}, {}, {}, {}
lc                                    = 0.1
x_, y_, z_, lc_, tag_                 = 0, 1, 2, 3, 4

# ------------------------------------------------- #
# --- [3] Modeling                              --- #
# ------------------------------------------------- #




# ------------------------------------------------- #
# --- [4] Physical Grouping                     --- #
# ------------------------------------------------- #
gmsh.model.occ.synchronize()
surfPhys["surf1"] = gmsh.model.addPhysicalGroup( surfDim, [ surf["sur"] ], tag=201 )
voluPhys["volu1"] = gmsh.model.addPhysicalGroup( voluDim, [ volu["vol"] ], tag=301 )


# ------------------------------------------------- #
# --- [2] post process                          --- #
# ------------------------------------------------- #
gmsh.model.occ.synchronize()
gmsh.model.mesh.generate(2)
gmsh.write( "model.geo_unrolled" )
gmsh.write( "model.msh" )
gmsh.finalize()

