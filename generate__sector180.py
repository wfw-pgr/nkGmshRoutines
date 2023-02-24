import sys
import numpy         as np
import gmsh
# import gmsh_api.gmsh as gmsh
import nkGmshRoutines.generate__sector90 as s90
import nkGmshRoutines.generate__hexaSector as h90

# ========================================================= #
# ===  generate half moon Shape  180 degree             === #
# ========================================================= #
def generate__sector180( lc=None, r1=0.0, r2=1.0, side="+", tag=-1, fuse=False, \
                         origin=[0.0,0.0], zoffset=0.0, height=1.0, hexahedral=False, \
                         defineSurf=False, defineVolu=False, numElements=[], recombine=False ):

    
    # ------------------------------------------------- #
    # --- [1] call sector90 twice                   --- #
    # ------------------------------------------------- #
    if ( hexahedral is False ):
        if ( side=="+" ):
            ret1 = s90.generate__sector90( lc=lc, r1=r1, r2=r2, quadrant=1, \
                                           origin=origin, zoffset=zoffset, height=height, \
                                           defineSurf=defineSurf, defineVolu=defineVolu, \
                                           recombine=recombine, numElements=numElements )
            ret2 = s90.generate__sector90( lc=lc, r1=r1, r2=r2, quadrant=4, \
                                           origin=origin, zoffset=zoffset, height=height, \
                                           defineSurf=defineSurf, defineVolu=defineVolu, \
                                           recombine=recombine, numElements=numElements )
        if ( side=="-" ):
            ret1 = s90.generate__sector90( lc=lc, r1=r1, r2=r2, quadrant=2, \
                                           origin=origin, zoffset=zoffset, height=height, \
                                           defineSurf=defineSurf, defineVolu=defineVolu, \
                                           recombine=recombine, numElements=numElements )
            ret2 = s90.generate__sector90( lc=lc, r1=r1, r2=r2, quadrant=3, \
                                           origin=origin, zoffset=zoffset, height=height, \
                                           defineSurf=defineSurf, defineVolu=defineVolu, \
                                           recombine=recombine, numElements=numElements )
        ret = [ ret1, ret2 ]

    else:
        if ( side=="+" ):
            ret1 = h90.generate__hexaSector( lc=lc, r1=r1, r2=r2, th1=0.0, th2=90.0, \
                                             origin=origin, zoffset=zoffset, height=height, \
                                             defineSurf=defineSurf, defineVolu=defineVolu, \
                                             numElements=numElements )
            ret2 = h90.generate__hexaSector( lc=lc, r1=r1, r2=r2, th1=270.0, th2=360.0, \
                                             origin=origin, zoffset=zoffset, height=height, \
                                             defineSurf=defineSurf, defineVolu=defineVolu, \
                                             numElements=numElements )
        if ( side=="-" ):
            ret1 = h90.generate__hexaSector( lc=lc, r1=r1, r2=r2, th1=90.0, th2=180.0, \
                                             origin=origin, zoffset=zoffset, height=height, \
                                             defineSurf=defineSurf, defineVolu=defineVolu, \
                                             numElements=numElements )
            ret2 = h90.generate__hexaSector( lc=lc, r1=r1, r2=r2, th1=-90.0, th2=-180.0, \
                                             origin=origin, zoffset=zoffset, height=height, \
                                             defineSurf=defineSurf, defineVolu=defineVolu, \
                                             numElements=numElements )
        ret = [ ret1, ret2 ]

    if ( fuse ):
        if ( defineVolu ):
            targets = [ (3, (ret1["volu"])["sector"] ) ]
            tools   = [ (3, (ret2["volu"])["sector"] ) ]
        elif ( defineSurf ):
            targets = [ (2, (ret1["surf"])["sector"] ) ]
            tools   = [ (2, (ret2["surf"])["sector"] ) ]
        else:
            sys.exit( "ERROR vol or surf" )
        ret = gmsh.model.occ.fuse( targets, tools, tag=tag, removeObject=True, removeTool=True )
        ret = ret[0]
        
    return( ret )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generate__sector180( r1=0.5, r2=1.0, height=0.4, lc=0.05, side="+", \
                         defineVolu=True, hexahedral=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.msh" )
    gmsh.finalize()
