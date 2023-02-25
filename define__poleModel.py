import numpy as np
import os, sys, time
import gmsh

# ========================================================= #
# ===  define__poleModel.py                             === #
# ========================================================= #

def define__poleModel( dimtags={}, const=None, cnsFile=None, \
                       mesh2dFile="msh/poleSurface_2d.msh", \
                       mesh3dFile="msh/poleSurface_3d.msh", \
                       interpolateData=None, interpolateFile=None, \
                       function=None, func_params=[], \
                       expandFile="msh/poleSurface_3d_expand.msh" ):

    x_, y_, z_ = 0, 1, 2
    dim_, tag_ = 0, 1
    sDim, vDim = 2, 3
    stime      = time.perf_counter()

    # ------------------------------------------------- #
    # --- [1] preparation                           --- #
    # ------------------------------------------------- #
    if ( const is None ):
        if ( cnsFile is not None ):
            import nkUtilities.load__constants as lcn
            const   = lcn.load__constants( inpFile=cnsFile )
        else:
            sys.exit( "\033[31m" + "[define__poleModel.py] const == ???" + "\033[0m" )
    GapLength  = ( const["geometry.z_gapMax"] - const["geometry.z_gapMin"] ) * 1.2
    flatShape  =   const["geometry.flat_pole"]
    if ( ( interpolateFile is None ) and ( function is None ) ):
        print( "\033[31m" + "[define__poleModel.py] interpolateFile or function  "\
               "should be given.... [ERROR]" + "\033[0m" )
        sys.exit()
    
    # ------------------------------------------------- #
    # --- [2] if flat mode                          --- #
    # ------------------------------------------------- #
    if ( flatShape ):
        dimtags   = define__baseVolume( const=const, flatShape=flatShape )
        return( dimtags )

    # ------------------------------------------------- #
    # --- [3] define pole surface coordinate        --- #
    # ------------------------------------------------- #
    import define__poleSurface_2d as ps2
    ps2.define__poleSurface_2d( const=const )
    
    # ------------------------------------------------- #
    # --- [2] setup pole surface                    --- #
    # ------------------------------------------------- #
    if ( interpolateFile is not None ):
        import nkUtilities.load__pointFile as lpf
        interpolateData = lpf.load__pointFile( inpFile=interpolateFile, returnType="point" )
    import nkMeshRoutines.modify__2Dmesh_into_3Dmesh as m23
    m23.modify__2Dmesh_into_3Dmesh( inpFile=mesh2dFile, outFile=mesh3dFile, ref_="z", \
                                    interpolateData=interpolateData, \
                                    function=function, parameters=func_params )

    # ------------------------------------------------- #
    # --- [3] modify pole surface 3D to expand      --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.expand__boundarySurface_in2DMesh as ebs
    ebs.expand__boundarySurface_in2DMesh( inpFile=mesh3dFile, outFile=expandFile )
    
    # ------------------------------------------------- #
    # --- [3] load 2D mesh and extrude for boolean  --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.importSurface__mesh2geom as m2g
    surfs      = m2g.importSurface__mesh2geom( inpFile=expandFile )
    extruded   = gmsh.model.occ.extrude( surfs, 0,0, (-1.0)*GapLength )
    volus      = [ dimtag for dimtag in extruded if ( dimtag[dim_] == vDim ) ]
    if ( len( volus ) > 2 ):
        ext, _ = gmsh.model.occ.fuse( [ volus[0] ], volus[1:] )
    else:
        print( "\033[31m" + "[define__poleModel.py] [CAUTION] extruded"\
               " volume has only 1 entity..." + "\033[0m" )

    # ------------------------------------------------- #
    # --- [4] define base volume & boolean          --- #
    # ------------------------------------------------- #
    baseVols  = define__baseVolume( const=const, flatShape=flatShape )
    gap, fmp  = gmsh.model.occ.intersect( baseVols["pole.gap&tip"], ext, \
                                          removeObject=False, removeTool=True  )
    tip, fmp  = gmsh.model.occ.cut      ( baseVols["pole.body"], gap, \
                                          removeObject=True , removeTool=False )

    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    dimtags   = { "pole.gap":gap, "pole.tip":tip, "pole.body":baseVols["pole.body"] }
    duration  = time.perf_counter() - stime
    h,m,s    = int(duration)//3600, (int(duration)%3600)//60, int(duration)%60
    print( "\n" + "-----"*16 )
    print( "[define__poleModel.py] elapssed time :: {0:02}:{1:02}:{2:02}".format( h,m,s ) )
    print( "-----"*16 + "\n" )
    return( dimtags )



# ========================================================= #
# ===  define__baseVolume                               === #
# ========================================================= #

def define__baseVolume( const=None, flatShape=False ):

    # ------------------------------------------------- #
    # --- [1] variables                             --- #
    # ------------------------------------------------- #
    r1     =   const["geometry.r_pole"]
    height =   const["geometry.h_iair1"]+const["geometry.h_coil"]+const["geometry.h_iair2"]
    dz1    =   const["geometry.z_gap"]
    dz2    =   const["geometry.z_pole"]
    dz3    =   height - dz1 - dz2
    zc1    =   0.0
    zc2    =   dz1
    zc3    =   dz1 + dz2

    # ------------------------------------------------- #
    # --- [2] theta by side                         --- #
    # ------------------------------------------------- #
    if   ( const["general.side"].lower() in [ "+-", "-+" ] ):
        th1, th2 =   0.0, +360.0
    elif ( const["general.side"].lower() in [ "+" ]        ):
        th1, th2 = -90.0,  +90.0
    elif ( const["general.side"].lower() in [ "-" ]        ):
        th1, th2 = +90.0, +270.0
    else:
        print( "[define__poleModel.py] unknwon mode  " )
        sys.exit()

    # ------------------------------------------------- #
    # --- [3] define volumes                        --- #
    # ------------------------------------------------- #
    if ( flatShape ):
        table = { "pole.gap"    : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc1, \
                                    "r0":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz1], "volume":True }, \
                  "pole.tip"    : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc2, \
                                    "r0":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz2], "volume":True }, \
                  "pole.body"   : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc3, \
                                    "r0":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz3], "volume":True } }
    else:
        table = { "pole.gap&tip": { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc1, \
                                    "r0":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz1+dz2], "volume":True }, \
                  "pole.body"   : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc3, \
                                    "r0":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz3    ], "volume":True } }
    import nkGmshRoutines.geometrize__fromTable as gft
    ret = gft.geometrize__fromTable( table=table )

    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #
    return( ret )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    # const                                       = {}
    # const["general.side"]                       = "+-"
    # const["geometry.r_pole"]                    = 1.050
    # const["geometry.z_gap"]                     = 0.100
    # const["geometry.z_pole"]                    = 0.275
    # const["geometry.h_iair1"]                   = 0.25034
    # const["geometry.h_coil"]                    = 0.11239
    # const["geometry.h_iair2"]                   = 0.10327
    # const["geometry.z_gapMin"]                  = 0.013
    # const["geometry.z_gapMax"]                  = 0.195
    # const["geometry.flat_pole"]                 = False
    # const["geometry.pole.meshType"]             = "direct-math"
    # const["geometry.pole.meshsize1"]            = 0.0125
    # const["geometry.pole.meshsize2"]            = 0.0500
    # const["geometry.pole.direct-math.mathEval"] = "(0.05/((sqrt(x^2+y^2)/1.05)^10+1))*Max(1/((sqrt(x^2+y^2)/0.9)^100+1),Min(1,2^(-20*x)*2^(20*y)+0.5))"
    
    import nkUtilities.load__constants as lcn
    cnsFile         = "dat/unified.conf"
    const           = lcn.load__constants( inpFile=cnsFile )
    
    interpolateFile = None
    function        = lambda x,y,c1,c2: (c1-c2) * np.sqrt( x**2 + y**2 ) + c2
    func_params     = [ const["geometry.z_gapMin"], const["geometry.z_gapMax"] ]
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    dimtags = {}
    dimtags = define__poleModel( const=const, dimtags=dimtags, \
                                 interpolateFile=interpolateFile, \
                                 function=function, func_params=func_params )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = False         # from nkGMshRoutines/test/mesh.conf, phys.conf
    uniform_size     = 0.05
    if ( mesh_from_config ):
        meshFile = "dat/mesh.conf"
        physFile = "dat/phys.conf"
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile, dimtags=dimtags )
    else:
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( uniform=uniform_size, dimtags=dimtags )
        
    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()


# ------------------------------------------------- #
# --- dev                                       --- #
# ------------------------------------------------- #

# import nkUtilities.equiSpaceGrid as esg
# x1MinMaxNum = [ -1.0, 1.0, 31 ]
# x2MinMaxNum = [ -1.0, 1.0, 31 ]
# x3MinMaxNum = [  0.0, 0.0,  1 ]
# interpolateData  = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
#                                       x3MinMaxNum=x3MinMaxNum, returnType = "point" )
# function   = lambda x,y,r: (-0.12)*np.sqrt( 1.0+np.round( (x/r)**2+(y/r)**2, 10 ) ) + 0.2
# parameters = [ 1.0 ]
# interpolateData[:,z_]  = function( interpolateData[:,x_], interpolateData[:,y_], *parameters )
# import nkMeshRoutines.modify__2Dmesh_into_3Dmesh as m23
# m23.modify__2Dmesh_into_3Dmesh( inpFile=mesh2dFile, outFile=mesh3dFile, ref_="z", \
#                                 function=function, parameters=parameters )
