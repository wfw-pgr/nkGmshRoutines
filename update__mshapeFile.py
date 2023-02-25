import numpy as np
import nkBasicAlgs.execute__commands as exe

# ========================================================= #
# ===  update__mshapeFile.py                            === #
# ========================================================= #

def update__mshapeFile( mshapeFile=None, const=None, cnsFile=None, \
                        outFile="dat/mshape_ibd.dat", jobDir=None ):

    x_, y_, z_, z0_ = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( const      is None ):
        if ( cnsFile is not None ):
            import nkUtilities.load__constants as lcn
            const   = lcn.load__constants( inpFile=cnsFile )
        else:
            sys.exit( "[update__mshapeFile.py] const == ???" )
    if ( jobDir is None ):
        sys.exit( "[update__mshapeFile.py] jobDir == ??? " )
            
    # ------------------------------------------------- #
    # --- [2] load mshape file                      --- #
    # ------------------------------------------------- #
    if ( mshapeFile is None ):
        sys.exit( "[update__mshapeFile.py] mshapeFile == ???" )
    else:
        import nkUtilities.load__pointFile as lpf
        mshape = lpf.load__pointFile( inpFile=mshapeFile, returnType="structured" )
        
    # ------------------------------------------------- #
    # --- [3] weakly modify mshape                  --- #
    # ------------------------------------------------- #
    if ( const["geometry.weak_modify"] is not None ):
        # -- [3-1] weak_modify * diff = delta        -- #
        mshape[...,z_ ] = mshape[...,z0_] + const["geometry.weak_modify"] * ( mshape[...,z_] - mshape[...,z0_] )
        mshape[...,z0_] = np.copy( mshape[...,z_] )     # --- to prevent weakly modifying twice. --- #
        
        # -- [3-2] save mshape into mshapeFile       -- #
        import nkUtilities.save__pointFile as spf
        spf.save__pointFile( outFile=mshapeFile, Data=Data )
        
        # -- [3-3] copy back to the original file   --- #
        commands = [ "cp {0} {1}dat/mshape_svd.dat".format( mshapeFile, jobDir ) ]
        exe.execute__commands( commands=commands )

    # ------------------------------------------------- #
    # --- [4] intrude boundary conditioning         --- #
    # ------------------------------------------------- #
    import nkBasicAlgs.intrude__boundary as ibd
    size     = ( mshape.shape[1], mshape.shape[2], 6 )
    mshape_  = np.reshape( mshape, size )
    ret      = ibd.intrude__boundary( Data=mshape_ )
    ret      = np.copy( mshape_ )
    mshape_ibd  = ret[:,x_:z_+1]
    import nkUtilities.save__pointFile as spf
    spf.save__pointFile( outFile=outFile, Data=mshape_ibd )

    return()


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #
if ( __name__=="__main__" ):

    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum  = [ -1.0, 1.0, 21 ]
    x2MinMaxNum  = [ -1.0, 1.0, 21 ]
    x3MinMaxNum  = [  1.0, 1.0,  1 ]
    coord        = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                      x3MinMaxNum=x3MinMaxNum, returnType = "structured" )
    field        = np.zeros_like( coord )
    field[...,0] = coord[...,2] * 0.9
    Data         = np.concatenate( [coord,field], axis=3 )
    import nkUtilities.save__pointFile as spf
    outFile   = "dat/mshape_svd.dat"
    spf.save__pointFile( outFile=outFile, Data=Data )

    
    mshapeFile = "dat/mshape_svd.dat"
    cnsFile    = "dat/unified.conf"
    outFile    = "dat/mshape_ibd.dat"
    
    update__mshapeFile( mshapeFile=mshapeFile, cnsFile=cnsFile, outFile=outFile, )
