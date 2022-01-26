import sys, gmsh
import numpy as np

# ========================================================= #
# ===  generate XYplane Circle Arc Curve                === #
# ========================================================= #
def generateXYplaneArcCurve( radius=None, origin=[0.0,0.0], th1=0.0, th2=180.0, zoffset=0.0, lc=1.0, ysign="+" ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    pts      = {}
    Lines    = {}
    Surfaces = {}
    Volumes  = {}
    ret      = {}
    # ------------------------------------------------- #
    # --- [2] generate points                       --- #
    # ------------------------------------------------- #
    if ( th2 - th1 > 90.0 ):
        obtuse, acute = True, False
    else:
        obtuse, acute = False, True
    initNum       = 1
    x_, y_        = 0, 1
    pth1, pth2    = th1/180.0*np.pi, th2/180.0*np.pi
    xp1           = [ radius*np.cos(pth1), radius*np.sin(pth1) ]
    xp2           = [ radius*np.cos(pth2), radius*np.sin(pth2) ]
    pts["OP"]     = [ origin[x_], origin[y_], zoffset, lc, initNum ]
    pts["+x"]     = [    xp1[x_],    xp1[y_], zoffset, lc, initNum ]
    pts["-x"]     = [    xp2[x_],    xp2[y_], zoffset, lc, initNum ]
    if ( obtuse ):
        ang       = 0.5*(pth2-pth1) + pth1
        if   (  ( th2-th1 == 180.0 ) & ( ysign=="+" ) ):
            xp3   = [ + radius*np.cos( ang ), + radius*np.sin( ang ) ]
        elif (  ( th2-th1 == 180.0 ) & ( ysign=="-" ) ):
            xp3   = [ - radius*np.cos( ang ), - radius*np.sin( ang ) ]
        else:
            xp3   = [ + radius*np.cos( ang ), + radius*np.sin( ang ) ]
        pts["+y"] = [ xp3[x_], xp3[y_], zoffset, lc, initNum ]
    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )
    # ------------------------------------------------- #
    # --- [3] generate lines                        --- #
    # ------------------------------------------------- #
    if ( acute  ):
        Lines["line1"] = gmsh.model.occ.addCircleArc( pts["+x"][4], pts["OP"][4], pts["-x"][4] )
    if ( obtuse ):
        Lines["line1"] = gmsh.model.occ.addCircleArc( pts["+x"][4], pts["OP"][4], pts["+y"][4] )
        print( pts["+y"] )
        print( pts["OP"] )
        print( pts["-x"] )
        Lines["line2"] = gmsh.model.occ.addCircleArc( pts["+y"][4], pts["OP"][4], pts["-x"][4] )
    # ------------------------------------------------- #
    # --- [4] PostProcess                           --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "Lines":Lines, "Surfaces":Surfaces, "Volumes":Volumes }
    return( ret )


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generateXYplaneArcCurve( radius= 1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.write( "example.geo_unrolled" )
    gmsh.finalize()

