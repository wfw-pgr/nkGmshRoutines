import numpy as np
import gmsh
import os, sys

# ------------------------------------------------------- #
# -- generate cylindrical-like structure along z-axis. -- #
# --    1. revolve along z-axis                        -- #
# --    2. rotate  along z-axis                        -- #
# ------------------------------------------------------- #

# ========================================================= #
# ===  generate__cylindrical.py                         === #
# ========================================================= #

def generate__cylindrical( rI1=0.0, rI2=0.0, rO1=1.0, rO2=1.0, theta1=0.0, theta2=360.0, \
                           z1 =0.0, z2=None, length=1.0 ):

    x_,y_,z_          = 0, 1, 2
    surfDim, voluDim  = 2, 3

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( z2 is None ): z2 = z1 + length
    angle      = np.pi / 180.0 * ( theta2 - theta1 )
    xc,yc,zc   = 0.0, 0.0, z1
    dx,dy,dz   = 0.0, 0.0, z2-z1
    
    # ------------------------------------------------- #
    # --- [2] make coordinates                      --- #
    # ------------------------------------------------- #
    coords = np.array( [ [ rI1, 0.0, z1 ],
                         [ rO1, 0.0, z1 ],
                         [ rO2, 0.0, z2 ],
                         [ rI2, 0.0, z2 ] ] )
    
    # ------------------------------------------------- #
    # --- [3] addLine on a plane to rotate          --- #
    # ------------------------------------------------- #
    pts   = []
    lines = []
    for coord in coords:
        pts   += [ gmsh.model.occ.addPoint( coord[x_], coord[y_], coord[z_] ) ]
    for iL in range(len(pts)-1):
        lines += [ gmsh.model.occ.addLine( pts[iL], pts[iL+1] ) ]
    lines   += [ gmsh.model.occ.addLine( pts[-1], pts[0] ) ]
    wireTag  = gmsh.model.occ.addCurveLoop   ( lines   )
    rotSurf  = gmsh.model.occ.addPlaneSurface( [ wireTag ] )
    rotSurf  = [(surfDim,rotSurf)]
    revolved = gmsh.model.occ.revolve( rotSurf, xc,yc,zc, dx,dy,dz, angle )
    dimtags  = [ (voluDim,revolved[1][1]) ]
    if ( ( theta1 != 0.0 ) and ( angle != 2.0*np.pi ) ):
        gmsh.model.occ.rotate( dimtags  , xc,yc,zc, dx,dy,dz, theta1*np.pi/180.0 )
    gmsh.model.occ.remove( rotSurf )
    gmsh.model.occ.synchronize()
    return( dimtags )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    dimtags = {}
    dimtags = generate__cylindrical( rI1=0.2, rI2=0.5, rO1=1.2, rO2=1.5, \
                                     theta1=45.0, theta2=315.0, z1=1.0, z2=1.5 )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = False         # from nkGMshRoutines/test/mesh.conf, phys.conf
    if ( mesh_from_config ):
        meshFile = "test/mesh.conf"
        physFile = "test/phys.conf"
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile, dimtags=dimtags )
    else:
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( uniform=0.05, dimtags=dimtags )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()

