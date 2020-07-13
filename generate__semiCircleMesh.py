import numpy as np
import os, sys
import gmsh_api.gmsh as gmsh
import nkGmshRoutines.generate__sectorShape as sct


# ========================================================= #
# ===  generate semi-circle Mesh                        === #
# ========================================================= #
def generate__semiCircleMesh( lc1=0.01, lc2=0.05, lc3=0.1, radius=1.0, origin=[0.0,0.0], \
                              th1=-90.0,th2=+90.0, zoffset=0.0, side="+" ):

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
    x_, y_, z_, lc_, tag_                 = 0, 1, 2, 3, 4

    # ------------------------------------------------- #
    # --- [3] Modeling                              --- #
    # ------------------------------------------------- #

    initNum       = 1
    x_, y_        = 0, 1
    pth1, pth2    = th1/180.0*np.pi, th2/180.0*np.pi
    xp1           = [ origin[x_]+radius*np.cos(pth1), origin[y_]+radius*np.sin(pth1) ]
    xp2           = [ origin[x_]+radius*np.cos(pth2), origin[y_]+radius*np.sin(pth2) ]
    pts["OP"]     = [ origin[x_], origin[y_], zoffset, lc2, initNum ]
    pts["P1"]     = [    xp1[x_],    xp1[y_], zoffset, lc1, initNum ]
    pts["P2"]     = [    xp2[x_],    xp2[y_], zoffset, lc3, initNum ]

    ang       = 0.5*(pth2-pth1) + pth1
    if   (  ( th2-th1 == 180.0 ) & ( side=="+" ) ):
        xp3   = [ origin[x_] + radius*np.cos( ang ), origin[y_] + radius*np.sin( ang ) ]
    elif (  ( th2-th1 == 180.0 ) & ( side=="-" ) ):
        xp3   = [ origin[x_] - radius*np.cos( ang ), origin[y_] - radius*np.sin( ang ) ]
    else:
        xp3   = [ origin[x_] + radius*np.cos( ang ), origin[y_] + radius*np.sin( ang ) ]
    pts["P3"] = [ xp3[x_], xp3[y_], zoffset, lc2, initNum ]

    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )

    line["arc1"] = gmsh.model.occ.addCircleArc( pts["P1"][4], pts["OP"][4], pts["P3"][4] )
    line["arc2"] = gmsh.model.occ.addCircleArc( pts["P3"][4], pts["OP"][4], pts["P2"][4] )

    line["diameter1"] = gmsh.model.occ.addLine( pts["OP"][4], pts["P1"][4] )
    line["diameter2"] = gmsh.model.occ.addLine( pts["P2"][4], pts["OP"][4] )

    LineLoop   = [ + line["diameter1"], + line["arc1"],   \
                   + line["arc2"]     , + line["diameter2"] ]
    LineLoopGroup  = gmsh.model.occ.addCurveLoop( LineLoop )
    surf["sector"] = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )

    # ------------------------------------------------- #
    # --- [4] Physical Grouping                     --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    surfPhys["semicircle"] = gmsh.model.addPhysicalGroup( surfDim, [ surf["sector"] ], tag=201 )

    # ------------------------------------------------- #
    # --- [5] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "model.geo_unrolled" )
    gmsh.write( "model.msh" )
    gmsh.finalize()



# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    generate__semiCircleMesh()


