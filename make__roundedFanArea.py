import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__roundedFanArea.py                          === #
# ========================================================= #

def make__roundedFanArea( r1=0.2, r2=0.3, theta1=1.0, theta2=30.0, \
                          nDiv_th=14, nDiv_r=14, nSkip_th=3, nSkip_r=3 ):
    
    # ------------------------------------------------- #
    # --- [1] make spline key points                --- #
    # ------------------------------------------------- #
    th1   = theta1 / 180.0 * np.pi
    th2   = theta2 / 180.0 * np.pi
    theta = np.linspace( th1, th2, nDiv_th )
    radii = np.linspace(  r1,  r2, nDiv_r  )
    
    #  -- [1-1] arc line 1 ( inner )                --  #
    xpt1  = r1 * np.cos( theta )
    ypt1  = r1 * np.sin( theta )
    i1,i2 = nSkip_th, min( nDiv_th-nSkip_th, nDiv_th-1 )
    xpt1  = xpt1[i1:i2]
    ypt1  = ypt1[i1:i2]

    #  -- [1-2] edge line 1                         --  #
    xpt2  = radii * np.cos( th2 )
    ypt2  = radii * np.sin( th2 )
    i1,i2 = nSkip_r, min( nDiv_r-nSkip_r, nDiv_r-1 )
    xpt2  = xpt2[i1:i2]
    ypt2  = ypt2[i1:i2]

    #  -- [1-3] arc line 2 ( outer )                --  #
    xpt3  = r2 * np.cos( theta[::-1] )
    ypt3  = r2 * np.sin( theta[::-1] )
    i1,i2 = nSkip_th, min( nDiv_th-nSkip_th, nDiv_th-1 )
    xpt3  = xpt3[i1:i2]
    ypt3  = ypt3[i1:i2]

    #  -- [1-4] edge line 2                         --  #
    xpt4  = radii[::-1] * np.cos( th1 )
    ypt4  = radii[::-1] * np.sin( th1 )
    i1,i2 = nSkip_r, min( nDiv_r-nSkip_r, nDiv_r-1 )
    xpt4  = xpt4[i1:i2]
    ypt4  = ypt4[i1:i2]

    #  -- [1-5] merge points                        --  #
    xpt   = np.concatenate( [ xpt1, xpt2, xpt3, xpt4 ] )
    ypt   = np.concatenate( [ ypt1, ypt2, ypt3, ypt4 ] )
    zpt   = np.zeros( (xpt.shape[0],) )
    xpt   = np.concatenate( [ xpt[:,None], ypt[:,None], zpt[:,None], ], axis=1 )

    # ------------------------------------------------- #
    # --- [2] make spline curve in gmsh             --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.make__splineCurve as msc
    ret   = msc.make__splineCurve( Data=xpt, addSurface=True )
    ret   = ( ret["surfs"] )["spline"]
    
    return( ret )

    


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 1 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 1 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    make__roundedFanArea()
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
        
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.01 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.01 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    



    # ------------------------------------------------- #
    # --- [3] display coordinate                    --- #
    # ------------------------------------------------- #
    # import nkUtilities.plot1D       as pl1
    # import nkUtilities.load__config as lcf
    # pngFile = "png/out.png"
    # config  = lcf.load__config()
    # fig     = pl1.plot1D( config=config, pngFile=pngFile )
    # fig.add__plot( xAxis=xpt[:,0], yAxis=xpt[:,1], linewidth=0, marker="x" )
    # fig.set__axis()
    # fig.save__figure()
