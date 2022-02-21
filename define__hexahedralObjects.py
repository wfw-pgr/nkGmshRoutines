import os, sys
import numpy as np
import gmsh
import nkGmshRoutines.generate__hexahedron as ghh
import nkGmshRoutines.generate__fanShape   as fan


# ========================================================= #
# ===  define__hexahedralObjects                        === #
# ========================================================= #

def define__hexahedralObjects( inpFile="dat/mc_cs.conf", blanket=True, returnType="list", \
                               r_margin=0.1, t_margin=0.1, z_margin=0.1, angle_offset=0.0 ):

    cs_, id_, th_, r1_, z1_, r2_, z2_, r3_, z3_, r4_, z4_ = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    voluDim = 3
    
    # ------------------------------------------------- #
    # --- [1] load mc position                      --- #
    # ------------------------------------------------- #
    import nkUtilities.load__pointFile as lpf
    Data = lpf.load__pointFile( inpFile=inpFile, returnType="point" )

    # ------------------------------------------------- #
    # --- [2] arange data                           --- #
    # ------------------------------------------------- #
    Data[:,th_]  = Data[:,th_] + angle_offset
    deg2rad      = np.pi / 180.0
    costh, sinth = np.cos( Data[:,th_]*deg2rad ), np.sin( Data[:,th_]*deg2rad )
    crossSection = [ [ Data[:,r1_]*costh, Data[:,r1_]*sinth, Data[:,z1_] ],
                     [ Data[:,r2_]*costh, Data[:,r2_]*sinth, Data[:,z2_] ], 
                     [ Data[:,r3_]*costh, Data[:,r3_]*sinth, Data[:,z3_] ], 
                     [ Data[:,r4_]*costh, Data[:,r4_]*sinth, Data[:,z4_] ] ]
    crossSection = np.array( crossSection )

    CSs          = np.array( Data[:,cs_], dtype=np.int64 )
    CStypes      = sorted( list( set( CSs ) ) )
    ids          = np.array( Data[:,id_], dtype=np.int64 ) # physical Numbers / entityNumbers
    idtypes      = sorted( list( set( ids ) ) )

    # ------------------------------------------------- #
    # --- [3] make hexahedron                       --- #
    # ------------------------------------------------- #
    hexas = {}
    for hCS in CStypes:
        index   = ( np.where( CSs == hCS ) )[0]
        cs      = crossSection[ :, :, index ]
        nCS     = cs.shape[2]
        retList = []
        for ik in range( nCS-1 ):
            vertex  = np.concatenate( [ cs[:,:,ik], cs[:,:,ik+1] ], axis=0 )
            ret     = ghh.generate__hexahedron( vertex=vertex, defineVolu=True, defineSurf=True )
            retList.append( ( voluDim,ret ) )
        hexas[ "cs={0:04}".format( hCS ) ] = retList
    
    # ------------------------------------------------- #
    # --- [4] fuse objects                          --- #
    # ------------------------------------------------- #
    named = {}
    for ik,hCS in enumerate( CStypes ):
        key     = "cs={0:04}".format( hCS )
        dimtags = hexas[key]
        if ( len( dimtags ) >= 2 ):
            targets     = [ dimtags[0] ]
            tools       =   dimtags[1:]
            ret, fmap   = gmsh.model.occ.fuse( targets, tools )
            named[key]  = ret
        else:
            named[key]  = dimtags

    # ------------------------------------------------- #
    # --- [5] fuse objects by physNums              --- #
    # ------------------------------------------------- #
    id_CS_table  = {}
    for Data_loc in Data:
        key = "id={0:04}".format(  int( Data_loc[id_] ) )
        if ( key in id_CS_table ):
            id_CS_table[key]  += [ int( Data_loc[cs_] ) ]
        else:
            id_CS_table[key]   = [ int( Data_loc[cs_] ) ]
    for key in list( id_CS_table.keys() ):
        id_CS_table[key] = list( set( id_CS_table[key] ) )
        
    volu   = []
    named_ = {}
    for ik,hid in enumerate( idtypes ):
        key     = "id={0:04}".format( hid )
        cs_loc  = id_CS_table[key]
        dimtags = [ ( named["cs={0:04}".format( hcs )] )[0] for hcs in cs_loc ]
        
        if   ( len( dimtags ) == 1 ):
            volu        += dimtags
            named_[key]  = dimtags
        elif ( len( dimtags ) >= 2 ):
            targets      = [ dimtags[0] ]
            tools        =   dimtags[1:]
            ret, fmap    = gmsh.model.occ.fuse( targets, tools )
            volu        += ret
            named_[key]  = ret
        else:
            sys.exit( "[define__hexahedralObjects.py] num of cs number is less than 1, at physical Number :: {0} ".format( hid ) )
    named = named_
    
    # ------------------------------------------------- #
    # --- [5] generate blancket                     --- #
    # ------------------------------------------------- #
    if ( blanket ):
        # ------------------------------------------------- #
        # --- [5-1] inquire min./max. of hexahedrons    --- #
        # ------------------------------------------------- #
        rMin     =    min( np.min( Data[:,r1_] ), np.min( Data[:,r3_] ) )
        rMax     =    max( np.max( Data[:,r2_] ), np.max( Data[:,r4_] ) )
        zMin     =    min( np.min( Data[:,z1_] ), np.min( Data[:,z2_] ) )
        zMax     =    min( np.max( Data[:,z3_] ), np.max( Data[:,z4_] ) )
        tMin     = np.min( Data[:,th_] )
        tMax     = np.max( Data[:,th_] )
        # ------------------------------------------------- #
        # --- [5-2] generate blanket model              --- #
        # ------------------------------------------------- #
        radius1  = max( rMin - ( rMax - rMin )*r_margin, 0.0 )
        radius2  =      rMax + ( rMax - rMin )*r_margin
        theta1   =      tMin - ( tMax - tMin )*t_margin
        theta2   =      tMax + ( tMax - tMin )*t_margin
        zoffset  = max( zMin - ( zMax - zMin )*z_margin, 0.0 )
        height   =    ( zMax + ( zMax - zMin )*z_margin      ) - zoffset
        blanket  = fan.generate__fanShape( r1     =radius1, r2    =radius2, \
                                           th1    =theta1 , th2   =theta2 , \
                                           zoffset=zoffset, height=height , \
                                           defineVolu=True )
        blanket  = blanket["volu"]["fan"]
        # ------------------------------------------------- #
        # --- [5-3] boolean blanket                     --- #
        # ------------------------------------------------- #
        target            = [ (voluDim,blanket) ]
        tools             = volu
        blanket,fmap      = gmsh.model.occ.cut( target, tools, removeObject=True, removeTool=False )
        volu             += blanket
        named["blanket"]  = blanket
        
    # ------------------------------------------------- #
    # --- [6] return volume                         --- #
    # ------------------------------------------------- #
    if   ( returnType.lower() == "list" ):
        return( volu  )
    elif ( returnType.lower() == "dict" ):
        return( named )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal" , 1 )
    gmsh.option.setNumber( "General.Verbosity", 3 )
    gmsh.option.setNumber( "Mesh.Algorithm"   , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D" , 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    ret = define__hexahedralObjects( inpFile="test/mc_cs.conf", returnType="dict" )
    print( ret )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.005 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.005 )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/mcModel.msh" )
    print( ret )
    gmsh.finalize()
