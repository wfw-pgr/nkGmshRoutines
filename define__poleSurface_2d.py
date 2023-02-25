import numpy as np
import os, sys
import gmsh


# ========================================================= #
# ===  define__poleSurface_coordinate                   === #
# ========================================================= #

def define__poleSurface_coordinate( const=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( const is None ): sys.exit( "[define__poleSurface_2d.py] const == ???" )

    # ------------------------------------------------- #
    # --- [2] parameter check                       --- #
    # ------------------------------------------------- #
    r0 = const["geometry.r_pole"]

    # ------------------------------------------------- #
    # --- [3] geometry making                       --- #
    # ------------------------------------------------- #
    if   ( const["general.side"].lower() in [ "+"] ):
        th1, th2 = -90.0, +90.0
    elif ( const["general.side"].lower() in [ "-"] ):
        th1, th2 = +90.0, 270.0
    elif ( const["general.side"].lower() in [ "+-", "-+" ] ):
        th1, th2 =   0.0, 360.0

    table   = { "region": { "geometry_type":"circleArc", \
                            "x0":0.0, "y0":0.0, "z0":0.0, \
                            "r0":r0, "th1":th1, "th2":th2, \
                            "surface":True } }
    import nkGmshRoutines.geometrize__fromTable as gft
    ret = gft.geometrize__fromTable( table=table )
    return( ret )


# ========================================================= #
# ===  define__poleSurface                              === #
# ========================================================= #

def define__poleSurface_2d( const=None, cnsFile=None, \
                            meshFile="dat/poleSurface_2d_mesh.conf", \
                            physFile="dat/poleSurface_2d_phys.conf", \
                            outFile="msh/poleSurface_2d.msh" ):
    
    # ------------------------------------------------- #
    # --- [0] arguments check                       --- #
    # ------------------------------------------------- #
    if ( const is None ):
        if ( cnsFile is not None ):
            import nkUtilities.load__constants as lcn
            const = lcn.load__constants( inpFile=cnsFile )
        else:
            sys.exit( "[define__poleSurface_2d.py] const == ???" )
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh_initialized = bool( gmsh.isInitialized() )
    if ( gmsh_initialized ):
        currentModel = gmsh.model.getCurrent()
    else:
        gmsh.initialize()
        gmsh.option.setNumber( "General.Terminal", 1 )
        gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
        gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
        gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "poleSurface2d" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    dimtags  = define__poleSurface_coordinate( const=const )
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh File settings                    --- #
    # ------------------------------------------------- #
    # -- set file contents -- #
    if ( const["geometry.pole.meshType"].lower() == "direct-math" ):
        evaluation = const["geometry.pole.direct-math.mathEval"]
    else:
        print( "\033[31m" + "[define__poleSurface_2d.py] under construction..." + "\033[0m" )
        sys.exit()
    entities      = ",".join( list( dimtags.keys() ) )
    physContents  = "# <names> key type dimtags_keys physNum\n"
    physContents += "region surf [{}] 201\n".format( entities )
    meshContents  = "# <names> key physNum meshType resolution1 resolution2 evaluation\n"
    meshContents += "region 201 {0} {1} {2} {3}\n"\
        .format( const["geometry.pole.meshType"] , const["geometry.pole.meshsize1"], \
                 const["geometry.pole.meshsize2"], evaluation )
    
    # -- write in a file -- #
    with open( physFile, "w" ) as f:
        f.write( physContents )
    with open( meshFile, "w" ) as f:
        f.write( meshContents )
    
    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = True         # from nkGMshRoutines/test/mesh.conf, phys.conf
    uniform_size     = 0.060
    if ( mesh_from_config ):
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile, \
                                       dimtags=dimtags )
    else:
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( uniform=uniform_size, dimtags=dimtags )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( outFile )
    if ( gmsh_initialized ):
        gmsh.model.remove()
        gmsh.model.setCurrent( currentModel )
        print( "\n" + "[define__poleSurface_2d.py] return to Model :: {} "\
               .format( currentModel ) + "\n" )
    else:
        gmsh.finalize()
    return()


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    cnsFile = "dat/unified.conf"
    define__poleSurface_2d( cnsFile=cnsFile )

    # const                                       = {}
    # const["geometry.r_pole"]                    = 1.050
    # const["general.side"]                       = "-"
    # const["geometry.pole.meshType"]             = "direct-math"
    # const["geometry.pole.meshsize1"]            = 0.0125
    # const["geometry.pole.meshsize2"]            = 0.0500
    # const["geometry.pole.direct-math.mathEval"] = "(0.05/((sqrt(x^2+y^2)/1.05)^10+1))*Max(1/((sqrt(x^2+y^2)/0.9)^100+1),Min(1,2^(-20*x)*2^(20*y)+0.5))"
    # define__poleSurface_2d( const=const )
