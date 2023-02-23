import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  define__poleModel.py                             === #
# ========================================================= #

def define__poleModel( dimtags={}, const=None, mesh2dFile="msh/poleSurface_2d.msh", \
                       mesh3dFile="msh/poleSurface_3d.msh", interpolateFile="dat/mshape_svd.dat", \
                       expandFile="msh/poleSurface_3d_expand.msh" ):

    x_, y_, z_ = 0, 1, 2
    dim_, tag_ = 0, 1
    sDim, vDim = 2, 3

    const            = {}
    const["pole.r0"] = 1.000
    const["pole.z0"] = 0.000
    const["pole.z1"] = 0.100
    const["pole.z2"] = 0.200
    const["pole.z3"] = 0.400
    const["mode"]    = "right"
    flatShape        = False

    # ------------------------------------------------- #
    # --- [1] preparation                           --- #
    # ------------------------------------------------- #
    if ( const is None ): sys.exit( "[define__poleModel.py] const == ???" )
    GapLength  = ( const["pole.z2"] - const["pole.z0"] ) * 1.2

    # ------------------------------------------------- #
    # --- [2] if flat mode                          --- #
    # ------------------------------------------------- #
    if ( flatShape ):
        dimtags   = define__baseVolume( const=const, flatShape=flatShape )
        return( dimtags )
    
    # ------------------------------------------------- #
    # --- [2] setup pole surface                    --- #
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
    import nkUtilities.load__pointFile as lpf
    Data    = lpf.load__pointFile( inpFile=interpolateFile, returnType="point" )
    import nkMeshRoutines.modify__2Dmesh_into_3Dmesh as m23
    m23.modify__2Dmesh_into_3Dmesh( inpFile=mesh2dFile, outFile=mesh3dFile, ref_="z", \
                                    interpolateData=interpolateData )

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
    dimtags   = { "pole.gap":gap, "pole.tip":tip, "pole.body":baseVols["pole.body"] }
    return( dimtags )


# ========================================================= #
# ===  define__baseVolume                               === #
# ========================================================= #

def define__baseVolume( const=None, flatShape=False ):

    r1               =   const["pole.r0"]
    dz1              = ( const["pole.z1"]-const["pole.z0"] )
    dz2              = ( const["pole.z2"]-const["pole.z1"] )
    dz3              = ( const["pole.z3"]-const["pole.z2"] )
    zc1              =   const["pole.z0"]
    zc2              =   const["pole.z1"]
    zc3              =   const["pole.z2"]
    
    if   ( const["mode"].lower() == "full"  ):
        th1, th2 =   0.0, +360.0
    elif ( const["mode"].lower() == "right" ):
        th1, th2 = -90.0,  +90.0
    elif ( const["mode"].lower() == "left"  ):
        th1, th2 = +90.0, +270.0
    else:
        print( "[define__poleModel.py] unknwon mode  " )
        sys.exit()

    if ( flatShape ):
        table = { "pole.gap"    : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc1, \
                                    "r1":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz1], "volume":True }, \
                  "pole.tip"    : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc2, \
                                    "r1":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz2], "volume":True }, \
                  "pole.body"   : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc3, \
                                    "r1":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz3], "volume":True } }
    else:
        table = { "pole.gap&tip": { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc1, \
                                    "r1":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz1+dz2], "volume":True }, \
                  "pole.body"   : { "geometry_type":"circleArc", \
                                    "x0":0.0, "y0":0.0, "z0":zc3, \
                                    "r1":r1, "th1":th1, "th2":th2, \
                                    "delta":[0,0,dz3    ], "volume":True } }
    import nkGmshRoutines.geometrize__fromTable as gft
    ret = gft.geometrize__fromTable( table=table )
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
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    sample__model = "make"     #  -- [ "import" / "make" ] --  #

    if   ( sample__model == "import" ):
        dimtagsFile = None
        stpFile     = "msh/model.stp"
        import nkGmshRoutines.import__stepFile as isf
        dimtags     = isf.import__stepFile( inpFile=stpFile, dimtagsFile=dimtagsFile )
        
    elif ( sample__model == "make"   ):
        dimtags = {}
        dimtags = define__poleModel( dimtags=dimtags )
        gmsh.model.occ.synchronize()
    
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
    print( dimtags )

