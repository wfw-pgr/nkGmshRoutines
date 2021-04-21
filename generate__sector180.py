import sys
import numpy         as np
import gmsh
# import gmsh_api.gmsh as gmsh
import nkGmshRoutines.generate__sector90 as s90

# ========================================================= #
# ===  generate half moon Shape  180 degree             === #
# ========================================================= #
def generate__sector180( lc=None, r1=0.0, r2=1.0, side="+", \
                         origin=[0.0,0.0], zoffset=0.0, height=1.0, \
                         defineSurf=False, defineVolu=False, numElements=[], recombine=False ):

    if ( recombine is True ):
        if ( len( numElements ) == 0 ):
            numElements = [ height/lc ]
        else:
            pass
    
    # ------------------------------------------------- #
    # --- [1] call sector90 twice                   --- #
    # ------------------------------------------------- #
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
    return( ret )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generate__sector180( r1=0.5, r2=1.0, height=0.4, lc=0.1, side="+", defineVolu=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.msh" )
    gmsh.finalize()
