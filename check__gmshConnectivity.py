import numpy as np
import os, sys, subprocess

# ========================================================= #
# ===  check__gmshConnectivity.py                       === #
# ========================================================= #

def check__gmshConnectivity():

    inpFile  = "msh/model.msh"
    
    # ------------------------------------------------- #
    # --- [1] convert into elmer format             --- #
    # ------------------------------------------------- #
    cmd = "ElmerGrid 14 2 {0}".format( inpFile )
    print( cmd )
    subprocess.call( cmd.split() )

    # ------------------------------------------------- #
    # --- [2] load element / node file              --- #
    # ------------------------------------------------- #
    
    dirname  = "/".join( ( inpFile.split( "/" ) )[:-1] )
    FileBase = ( ( inpFile.split( "/" ) )[-1] ).split( ".msh" )[0]
    
    elemFile = dirname + "/" + FileBase + "/" + "mesh.elements"
    nodeFile = dirname + "/" + FileBase + "/" + "mesh.nodes"

    with open( elemFile, "r" ) as f:
        elems = np.loadtxt( f, dtype=np.int64 )
        elems = elems[:,3:]
    with open( nodeFile, "r" ) as f:
        nodes = np.loadtxt( f, dtype=np.float )
        nodes = nodes[:,2:]

    # ------------------------------------------------- #
    # --- [3] calculate volume of the element       --- #
    # ------------------------------------------------- #
    nElems   = elems.shape[0]
    onesixth = 1.0 / 6.0
    volumes  = np.zeros( (nElems) )
    for iv,vert in enumerate( elems ):
        iv0,iv1,iv2,iv3 =    vert[0]-1,    vert[1]-1,    vert[2]-1,    vert[3]-1
        nd0,nd1,nd2,nd3 = nodes[iv0,:], nodes[iv1,:], nodes[iv2,:], nodes[iv3,:]
        vc1,vc2,vc3     =    nd1 - nd0,    nd2 - nd0,    nd3 - nd0
        matrix          = np.concatenate( [vc1[:,None],vc2[:,None],vc3[:,None]], axis=1 )
        volumes[iv]     = onesixth * np.linalg.det( matrix )

    # ------------------------------------------------- #
    # --- [4] output                                --- #
    # ------------------------------------------------- #
    #  -- [4-1] statistics                          --  #
    avgvol = np.average( volumes )
    stddev = np.std    ( volumes )
    print()
    print( "[check__gmshConnectivity.py]  --- check of the gmsh File --- " )
    print( "[check__gmshConnectivity.py]    #.of elements     :: {0}".format( nElems ) )
    print( "[check__gmshConnectivity.py]   average( volumes ) :: {0}".format( avgvol ) )
    print( "[check__gmshConnectivity.py]    stddev( volumes ) :: {0}".format( stddev ) )
    print()

    #  -- [4-2] output data                         --  #
    Data        = np.zeros( (nElems,6) )
    Data[:,0  ] = np.arange( 1,nElems+1 )
    Data[:,1:5] = np.copy( elems[:,:] )
    Data[:,5  ] = np.copy( volumes    )

    #  -- [4-3] negative volume elements            --  #
    index       = np.where( Data[:,5] <= 0.0 )
    illegal     = Data[index]

    #  -- [4-4] save in a file                      --  #
    import nkUtilities.save__pointFile as spf
    outFile1    = "dat/gmsh_check.dat"
    outFile2    = "dat/illegal_elements.dat"
    spf.save__pointFile( outFile=outFile1, Data=Data )
    spf.save__pointFile( outFile=outFile2, Data=illegal, \
                         fmt=["%12d","%12d","%12d","%12d","%12d","%15.8e"] )
    return()

    

# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    check__gmshConnectivity()
