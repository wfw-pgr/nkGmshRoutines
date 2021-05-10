import os, sys, math
import numpy         as np
import gmsh
# import gmsh_api.gmsh as gmsh


# ========================================================= #
# ===  generate Sector Shape ( ougi - gata ) 90 degree  === #
# ========================================================= #
def generate__hexaSector( lc=None, r1=0.0, r2=1.0, th1=0.0, th2=90.0, recombine=True, \
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
    pth1, pth2    = th1/180.0*np.pi, th2/180.0*np.pi
    angle         = pth2 - pth1

    if ( len( numElements ) == 0 ):
        numE1,numE2      = [ math.ceil( ( r2-r1 )/lc ) ], [ math.ceil( r2*angle/lc ) ]
        numE3            = [ math.ceil( height/lc )    ]
    else:
        numE1,numE2      = numElements, numElements
        numE3            = numElements

    #  -- [2-2] geometry making                     --  #
    initNum          = 1
    xc,yc,zc         = origin[x_], origin[y_], zoffset
    pts["OP"]        = [ xc, yc, zc, lc, initNum ]
    ( pts["OP"] )[4] = gmsh.model.occ.addPoint( (pts["OP"])[0], (pts["OP"])[1], \
                                                (pts["OP"])[2], meshSize=(pts["OP"])[3] )
    if ( r1 == 0.0 ):
        # -- [2-2-1] first line                     --  #
        dx,dy,dz         = r2*np.cos( pth1 ), r2*np.sin( pth1 ), 0.0
        ret              = gmsh.model.occ.extrude( [(0,(pts["OP"])[4])], dx,dy,dz, \
                                                   numElements=numE1, recombine=recombine )
        pts["P1"],line["L1"]  = ( ret[0] )[1], ( ret[1] )[1]
        # -- [2-2-2] curved arc / area              --  #
        ret              = gmsh.model.occ.revolve( [(1,line["L1"])], xc,yc,zc, 0,0,1, angle, \
                                                   numElements=numE2, recombine=recombine )
        line["L2"],surf["sector"],line["L3"] = ( ret[0] )[1], ( ret[1] )[1], ( ret[2] )[1]
        # -- [2-2-3] sector shape volume            --  #
        ret              = gmsh.model.occ.extrude( [ (2,surf["sector"])], 0.0, 0.0, height, \
                                                   numElements=numE3, recombine=recombine )
        volu["sector"]   = ret[1][1]

    #   -- [2-3] geometry making r1 > 0.0 case      --  #
    if ( r1 >  0.0 ):
        # -- [2-3-1]  first line                    --  #
        pts["P1"]        = [ xc+r1*np.cos(pth1), yc+r1*np.sin(pth1), zc, lc, initNum ]
        ( pts["P1"] )[4] = gmsh.model.occ.addPoint( (pts["P1"])[0], (pts["P1"])[1], \
                                                    (pts["P1"])[2], meshSize=(pts["P1"])[3] )
        dx,dy,dz         = (r2-r1)*np.cos( pth1 ), (r2-r1)*np.sin( pth1 ), 0.0
        ret              = gmsh.model.occ.extrude( [(0,(pts["P1"])[4])], dx,dy,dz, \
                                                   numElements=numE1, recombine=recombine )
        line["L1"]       = ( ret[1] )[1]
        # -- [2-3-2] curved arc / area              --  #
        ret              = gmsh.model.occ.revolve( [(1,line["L1"])], xc,yc,zc, 0,0,1, angle, \
                                                   numElements=numE2, recombine=recombine )
        surf["sector"]   = ( ret[1] )[1]
        # -- [2-2-3] sector shape volume            --  #
        ret              = gmsh.model.occ.extrude( [ (2,surf["sector"])], 0.0, 0.0, height, \
                                                   numElements=numE3, recombine=recombine )
        volu["sector"]   = ret[1][1]
        
        
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

    generate__hexaSector( r1=0.3, r2=1.0, lc=0.05, \
                          defineVolu=True, recombine=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/example.msh" )
    gmsh.finalize()
