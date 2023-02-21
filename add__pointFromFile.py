import numpy         as np
# import gmsh_api.gmsh as gmsh
import gmsh


# ========================================================= #
# ===  add_pointFromFile                                === #
# ========================================================= #

def add__pointFromFile( inpFile=None, pts=None, key="pts", lc=0.1 ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    
    x_, y_, z_, lc_, tag_ = 0, 1, 2, 3, 4

    if ( pts     is None ): pts = {}
    if ( inpFile is None ): sys.exit( "[add__pointFromFile] inpFile == ???" )

    # ------------------------------------------------- #
    # --- [2] Load Point File                       --- #
    # ------------------------------------------------- #
    
    with open( inpFile, "r" ) as f:
        rData = np.loadtxt( f )
    nData = rData.shape[0]
    nColm = rData.shape[1]

    if   ( nColm == 3 ):
        Data        = np.zeros( (nData,5) )
        Data[:,0:3] = rData
        Data[:,  3] = lc
        Data[:,  4] = 0
    elif ( nColm == 5 ):
        Data        = np.copy( rData )
        
    # ------------------------------------------------- #
    # --- [3] add point                             --- #
    # ------------------------------------------------- #
        
    for ik in range( nData ):
        hkey            = "{0}_{1:06}".format( key, ik )
        pts[hkey]       = [ Data[ik,x_], Data[ik,y_], Data[ik,z_], Data[ik,lc_], Data[ik,tag_] ]
        pts[hkey][tag_] = gmsh.model.occ.addPoint( pts[hkey][x_], pts[hkey][y_], pts[hkey][z_], meshSize=pts[hkey][lc_] )

    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #

    return( pts )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    lc      =  0.10
    pts     = {}
    inpFile = "test.dat"
    
    add__pointFromFile( lc=lc, inpFile=inpFile, key="test", pts=pts )

    print( pts )
    
    gmsh.model.occ.synchronize()
    gmsh.write( "example.geo_unrolled" )
    gmsh.finalize()


