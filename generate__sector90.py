import sys
import numpy         as np
import gmsh
# import gmsh_api.gmsh as gmsh

# ========================================================= #
# ===  generate Sector Shape ( ougi - gata ) 90 degree  === #
# ========================================================= #
def generate__sector90( lc=None, r1=0.0, r2=1.0, quadrant=1, recombine=False, \
                        origin=[0.0,0.0], zoffset=0.0, height=1.0, numElements=[], \
                        defineSurf=False, defineVolu=False ):

    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsDim, lineDim, surfDim, voluDim  =  0,  1,  2,  3
    pts   , line   , surf   , volu     = {}, {}, {}, {}
    x_, y_, z_, lc_, tag_              =  0,  1,  2,  3, 4
    if ( defineVolu ):
        defineSurf = True
    if ( lc is None ):
        lc = ( r2 - r1 ) / 10.0
    
    # ------------------------------------------------- #
    # --- [2] generate points                       --- #
    # ------------------------------------------------- #
    #  -- [2-1] angle settings                      --  #
    if   ( quadrant == 1 ):
        th1, th2 = 0.0, 90.0
    elif ( quadrant == 2 ):
        th1, th2 = 90.0, 180.0
    elif ( quadrant == 3 ):
        th1, th2 = 180.0, 270.0
    elif ( quadrant == 4 ):
        th1, th2 = 270.0, 360.0
    pth1, pth2    = th1/180.0*np.pi, th2/180.0*np.pi

    #  -- [2-2] point definition                    --  #
    initNum       = 1
    if   ( r1 == 0.0 ):
        xp1           = [ origin[x_]+r2*np.cos(pth1), origin[y_]+r2*np.sin(pth1) ]
        xp2           = [ origin[x_]+r2*np.cos(pth2), origin[y_]+r2*np.sin(pth2) ]
        pts["OP"]     = [ origin[x_], origin[y_], zoffset, lc, initNum ]
        pts["P1"]     = [    xp1[x_],    xp1[y_], zoffset, lc, initNum ]
        pts["P2"]     = [    xp2[x_],    xp2[y_], zoffset, lc, initNum ]
    else:
        xp1           = [ origin[x_]+r1*np.cos(pth1), origin[y_]+r1*np.sin(pth1) ]
        xp2           = [ origin[x_]+r1*np.cos(pth2), origin[y_]+r1*np.sin(pth2) ]
        xp3           = [ origin[x_]+r2*np.cos(pth2), origin[y_]+r2*np.sin(pth2) ]
        xp4           = [ origin[x_]+r2*np.cos(pth1), origin[y_]+r2*np.sin(pth1) ]
        pts["OP"]     = [ origin[x_], origin[y_], zoffset, lc, initNum ]
        pts["P1"]     = [    xp1[x_],    xp1[y_], zoffset, lc, initNum ]
        pts["P2"]     = [    xp2[x_],    xp2[y_], zoffset, lc, initNum ]
        pts["P3"]     = [    xp3[x_],    xp3[y_], zoffset, lc, initNum ]
        pts["P4"]     = [    xp4[x_],    xp4[y_], zoffset, lc, initNum ]

    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )
        
    # ------------------------------------------------- #
    # --- [3] generate lines                        --- #
    # ------------------------------------------------- #
    if ( r1 == 0.0 ):
        line["radii1"] = gmsh.model.occ.addLine( pts["OP"][4], pts["P1"][4] )
        line["radii2"] = gmsh.model.occ.addLine( pts["P2"][4], pts["OP"][4] )
        line["arc1"]   = gmsh.model.occ.addCircleArc( pts["P1"][4], pts["OP"][4], pts["P2"][4] )
    else:
        line["radii1"] = gmsh.model.occ.addLine( pts["P2"][4], pts["P3"][4] )
        line["radii2"] = gmsh.model.occ.addLine( pts["P4"][4], pts["P1"][4] )
        line["arc1"]   = gmsh.model.occ.addCircleArc( pts["P1"][4], pts["OP"][4], pts["P2"][4] )
        line["arc2"]   = gmsh.model.occ.addCircleArc( pts["P3"][4], pts["OP"][4], pts["P4"][4] )

    # ------------------------------------------------- #
    # --- [4] generate Areas                        --- #
    # ------------------------------------------------- #
    if ( defineSurf ):
        if ( r1 == 0.0 ):
            LineLoop   = [ +line["radii1"], line["arc1"], line["radii2"] ]
        else:
            LineLoop   = [ +line["arc1"], +line["radii1"], line["arc2"], line["radii2"] ]
        LineLoopGroup  = gmsh.model.occ.addCurveLoop( LineLoop )
        surf["sector"] = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )
    if ( defineVolu ):
        ret            = gmsh.model.occ.extrude( [ (2,surf["sector"])], 0.0, 0.0, height, \
                                                 numElements=numElements, recombine=recombine )
        volu["sector"] = ret[1][1]
        
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

    generate__sector90( r1=0.5, r2=1.0, lc=0.1, defineVolu=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

