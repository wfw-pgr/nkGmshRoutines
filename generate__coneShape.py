import sys
import numpy         as np
import gmsh_api.gmsh as gmsh


# ========================================================= #
# ===  generate cone Shape                              === #
# ========================================================= #
def generate__coneShape( lc=1.0, r1=1.0, r2=0.0, origin=[0.0,0.0,0.0], th1=0.0, th2=180.0,
                         height=1.0, side="+" ):
    
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsDim , lineDim , surfDim , voluDim  =  0,  1,  2,  3
    pts    , line    , surf    , volu     = {}, {}, {}, {}
    x_,y_,z_,lc_,tag_                     = 0, 1, 2, 3, 4
    if ( r2 == 0.0  ): cross_section = "triangle"
    th1, th2 = np.pi/180.0*th1, np.pi/180.0*th2
    if ( side == "-" ):
        th1, th2 = th1+np.pi, th2+np.pi
    
    # ------------------------------------------------- #
    # --- [2] generate points                       --- #
    # ------------------------------------------------- #
    initNum       = 1
    x_, y_        = 0, 1
    dx1, dy1      = r1*np.cos( th1 ), r1*np.sin( th1 )
    dx2, dy2      = r2*np.cos( th1 ), r2*np.sin( th1 )
    dz            = height
    pts["P0"]     = [ origin[x_]    , origin[y_]    , origin[z_]   , lc, initNum ]
    pts["P1"]     = [ origin[x_]+dx1, origin[y_]+dy1, origin[z_]   , lc, initNum ]
    pts["P2"]     = [ origin[x_]+dx2, origin[y_]+dy2, origin[z_]+dz, lc, initNum ]
    pts["P3"]     = [ origin[x_]    , origin[y_]    , origin[z_]+dz, lc, initNum ]
    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )
    
    # ------------------------------------------------- #
    # --- [3] generate lines                        --- #
    # ------------------------------------------------- #
    line["cs_01"] = gmsh.model.occ.addLine( pts["P0"][4], pts["P1"][4] )
    line["cs_12"] = gmsh.model.occ.addLine( pts["P1"][4], pts["P2"][4] )
    line["cs_23"] = gmsh.model.occ.addLine( pts["P2"][4], pts["P3"][4] )
    line["cs_30"] = gmsh.model.occ.addLine( pts["P3"][4], pts["P0"][4] )
        
    # ------------------------------------------------- #
    # --- [4] generate Areas                        --- #
    # ------------------------------------------------- #
    LineLoop      = [ + line["cs_01"], + line["cs_12"], line["cs_23"], line["cs_30"] ]
    LineLoopGroup = gmsh.model.occ.addCurveLoop( LineLoop )
    surf["cone"]  = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )
    angle         = th2 - th1
    ret           = gmsh.model.occ.revolve( [ (surfDim,surf["cone"])], \
                                           origin[0], origin[1], origin[2], \
                                           origin[0], origin[1], origin[2]+height, \
                                           angle )
    volu["cone"]  = ret[1][1]
    
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

    generate__coneShape( r1=1.0, r2=0.6, th1=0.0, th2=+90.0, lc=0.05 )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

