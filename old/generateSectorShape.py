import sys, gmsh
import numpy as np

# ========================================================= #
# ===  generate Sector Shape ( ougi - gata )            === #
# ========================================================= #
def generateSectorShape( radius=None, origin=[0.0,0.0], th1=0.0, th2=180.0, zoffset=0.0, lc=1.0, zWidth=1.0, \
                         defineDiameter=False, defineSurf=False, defineVolu=False, side="+" ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    pts      = {}
    line     = {}
    surf     = {}
    volu     = {}
    ret      = {}
    if ( defineVolu ): defineSurf    =True
    if ( defineSurf ): defineDiameter=True
        
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
    pts["P1"]     = [    xp1[x_],    xp1[y_], zoffset, lc, initNum ]
    pts["P2"]     = [    xp2[x_],    xp2[y_], zoffset, lc, initNum ]
    if ( obtuse ):
        ang       = 0.5*(pth2-pth1) + pth1
        if   (  ( th2-th1 == 180.0 ) & ( side=="+" ) ):
            xp3   = [ + radius*np.cos( ang ), + radius*np.sin( ang ) ]
        elif (  ( th2-th1 == 180.0 ) & ( side=="-" ) ):
            xp3   = [ - radius*np.cos( ang ), - radius*np.sin( ang ) ]
        else:
            xp3   = [ + radius*np.cos( ang ), + radius*np.sin( ang ) ]
        pts["P3"] = [ xp3[x_], xp3[y_], zoffset, lc, initNum ]
    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )
    # ------------------------------------------------- #
    # --- [3] generate lines                        --- #
    # ------------------------------------------------- #
    if ( acute  ):
        line["arc1"] = gmsh.model.occ.addCircleArc( pts["P1"][4], pts["OP"][4], pts["P2"][4] )
    if ( obtuse ):
        line["arc1"] = gmsh.model.occ.addCircleArc( pts["P1"][4], pts["OP"][4], pts["P3"][4] )
        line["arc2"] = gmsh.model.occ.addCircleArc( pts["P3"][4], pts["OP"][4], pts["P2"][4] )
    if ( defineDiameter ):
        line["diameter1"] = gmsh.model.occ.addLine( pts["OP"][4], pts["P1"][4] )
        line["diameter2"] = gmsh.model.occ.addLine( pts["P2"][4], pts["OP"][4] )
    # ------------------------------------------------- #
    # --- [4] generate Areas                        --- #
    # ------------------------------------------------- #
    if ( defineSurf ):
        if   ( acute  ):
            LineLoop   = [ + line["diameter1"], + line["arc1"], line["diameter2"] ]
        elif ( obtuse ):
            LineLoop   = [ + line["diameter1"], + line["arc1"],   \
                           + line["arc2"]     , line["diameter2"] ]
        LineLoopGroup  = gmsh.model.occ.addCurveLoop( LineLoop )
        surf["sector"] = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )
    if ( defineVolu ):
        volu["sector"] = gmsh.model.occ.extrude( [ (2,surf["sector"])], 0.0, 0.0, zWidth )
        
    # ------------------------------------------------- #
    # --- [5] PostProcess                           --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "line":line, "surf":surf, "volu":volu }
    return( ret )


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generateSectorShape( radius=1.0, th1=-90.0, th2=+90.0, defineSurf=True, lc=0.05, defineVolu=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

