import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  rotate__pointshape                               === #
# ========================================================= #

def rotate__pointshape( points=None, lc=0.0, angle=360.0, axis_xyz=[0.0,0.0,0.0], \
                        axis_vec=[0.0,0.0,1.0] ):

    x_,y_,z_ = 0, 1, 2
    angle    = angle / 180.0 * np.pi
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( points is None ): sys.exit( "[rotate__pointshape.py] points == ???" )
    if ( points[0] != points[-1] ):
        points = np.array( points )
        points = np.concatenate( [ points[:,:], np.reshape( points[0,:], (1,3) ) ], axis=0 )
    
    # ------------------------------------------------- #
    # --- [2] put points                            --- #
    # ------------------------------------------------- #
    pts = []
    for pt in points:
        pts.append( gmsh.model.occ.addPoint( pt[x_], pt[y_], pt[z_], meshSize=lc ) )
    lines = []
    for iL in range( len(pts)-1 ):
        lines.append( gmsh.model.occ.addLine( pts[iL], pts[iL+1] ) )
    LineLoopGroup = gmsh.model.occ.addCurveLoop( lines )
    surfs         = gmsh.model.occ.addPlaneSurface( [LineLoopGroup] )
    dimtags       = [(2,surfs)]
    ret           = gmsh.model.occ.revolve( dimtags, \
                                            axis_xyz[x_], axis_xyz[y_], axis_xyz[z_], \
                                            axis_vec[x_], axis_vec[y_], axis_vec[z_], angle )
    return( ret )

    
# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 1 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 1 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 1 )
    gmsh.model.add( "model" )

    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    points = [ [0.7, 0.0, 0.0],\
               [1.0, 0.0, 0.0],\
               [1.0, 0.0, 1.3],\
               [0.7, 0.0, 1.0],\
               [0.7, 0.0, 0.0] ]
    
    rotate__pointshape( points=points )
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    
    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    
