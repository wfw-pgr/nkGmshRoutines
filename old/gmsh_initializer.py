import numpy as np
import sys
import gmsh

# ------------------------------------------------- #
# --- [1] initialization of the gmsh            --- #
# ------------------------------------------------- #
gmsh.initialize()
gmsh.option.setNumber( "General.Terminal", 1 )
gmsh.option.setNumber( "Mesh.Algorithm"  , 2 )
gmsh.model.add( "model" )



# ------------------------------------------------- #
# --- [2] post process                          --- #
# ------------------------------------------------- #
gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(3)
gmsh.write( "model.geo_unrolled" )
gmsh.write( "model.msh" )
gmsh.finalize()
