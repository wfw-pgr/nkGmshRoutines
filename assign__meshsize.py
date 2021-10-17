import os, sys, re
import numpy         as np
# import gmsh_api.gmsh as gmsh
import gmsh

# ========================================================= #
# ===  assign mesh size ( main routine )                === #
# ========================================================= #
def assign__meshsize( meshsize_list=None, volumes_list=None, meshFile=None, physFile=None, \
                      target="volu" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    meshconfig = None
    if ( ( meshsize_list is None ) and ( volumes_list is None ) ):
        if   ( meshFile is None ):
            sys.exit( "[assign__meshsize] give meshFile or, volumes_list & meshsize_list" )
        elif ( physFile is None ):
            print( "[assign__meshsize.py] physFile == ??? " )
            sys.exit()
            # meshconfig    = load__meshconfig( meshFile=meshFile )
            # keys          = list( ( meshconfig[target] ).keys() )
            # volumes_list  = [ (meshconfig[target]     )[key] for key in keys ]
            # meshsize_list = [ (meshconfig["meshsize"])[key] for key in keys ]
        else:
            meshconfig     = load__mesh_and_phys_config( meshFile=meshFile, physFile=physFile )
            keys           = list( ( meshconfig[target] ).keys() )
            volumes_list   = [ (meshconfig[target]     )[key] for key in keys ]
            meshsize_list1 = [ (meshconfig["meshsize1"])[key] for key in keys ]
            meshsize_list2 = [ (meshconfig["meshsize2"])[key] for key in keys ]
            meshTypes      = [ (meshconfig["meshTypes"] )[key] for key in keys ]
            mathEvals      = [ (meshconfig["mathEvals"] )[key] for key in keys ]
            minMeshSize    = meshconfig["minMeshSize"]
            maxMeshSize    = meshconfig["maxMeshSize"]

    # ------------------------------------------------- #
    # --- [2] check entity numbers                  --- #
    # ------------------------------------------------- #
    itarget   = ( ["pts","line","surf","volu"] ).index( target )
    allEntities = gmsh.model.getEntities(itarget)
    allEntities = [ int(dimtag[1]) for dimtag in allEntities ]
    missing     = list( set( volumes_list ) - set( allEntities  ) )
    remains     = list( set( allEntities  ) - set( volumes_list ) )
    print( "[assign__meshsize.py] listed volume nums :: {0} ".format( volumes_list ) )
    print( "[assign__meshsize.py] all Entities       :: {0} ".format( allEntities  ) )
    print( "[assign__meshsize.py] remains            :: {0} ".format( remains      ) )

    if ( len( missing ) > 0 ):
        print( "[assign__meshsize.py] missing            :: {0} ".format( missing    ) )
        print( "[assign__meshsize.py] aborting           :: current.msh "       )
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", minMeshSize )
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", maxMeshSize )
        gmsh.model.mesh.generate(3)
        gmsh.write( "current.msh" )
        print( "[assign__meshsize.py] missing Entity Error STOP " )
        sys.exit()
    
                
    # ------------------------------------------------- #
    # --- [2] define each mesh field                --- #
    # ------------------------------------------------- #
    fieldlist = []
    for ik,vl in enumerate( volumes_list ):
        ms  = [ meshsize_list1[ik], meshsize_list2[ik] ]
        ret = assign__meshsize_on_each_volume( volume_num=vl, meshsize=ms, target=target, \
                                               meshType  =meshTypes[ik], \
                                               mathEval  =mathEvals[ik] )
        fieldlist.append( ret[1] )

    # ------------------------------------------------- #
    # --- [3] define total field                    --- #
    # ------------------------------------------------- #
    totalfield = gmsh.model.mesh.field.add( "Min" )
    gmsh.model.mesh.field.setNumbers( totalfield, "FieldsList", fieldlist )
    gmsh.model.mesh.field.setAsBackgroundMesh( totalfield )

    # ------------------------------------------------- #
    # --- [4] define Min Max size                   --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", minMeshSize )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", maxMeshSize )
    
    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "meshsize_list":meshsize_list1, "volumes_list":volumes_list, \
            "field_list":fieldlist }
    return( ret )
    


# ========================================================= #
# ===  assigne meshsize onto volume Entities            === #
# ========================================================= #
def assign__meshsize_on_each_volume( volume_num=None, meshsize=None, target="volu", \
                                     mathEval  =None, meshType=None ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( volume_num is None ): sys.exit( "[assign__meshsize_on_each_volume] volume_num == ??? " )
    if ( meshsize   is None ): sys.exit( "[assign__meshsize_on_each_volume] meshsize   == ??? " )
    if ( meshType   is None ): sys.exit( "[assign__meshsize_on_each_volume] meshType   == ??? " )
    itarget   = ( ["pts","line","surf","volu"] ).index( target )
    
    # ------------------------------------------------- #
    # --- [2] define MathEval Field                 --- #
    # ------------------------------------------------- #
    mathEval = acquire__mathEval( volume_num=volume_num, meshType=meshType, itarget=itarget, \
                                  meshsize  =meshsize  , mathEval=mathEval )
    
    fieldmath = gmsh.model.mesh.field.add( "MathEval" )
    gmsh.model.mesh.field.setString( fieldmath, "F", mathEval )
    
    # ------------------------------------------------- #
    # --- [3] define Restrict Field                 --- #
    # ------------------------------------------------- #
    if   ( target == "volu" ):
        dimtags_v = [(itarget,volume_num)]
        dimtags_s = gmsh.model.getBoundary( dimtags_v )
        dimtags_l = gmsh.model.getBoundary( dimtags_s, combined=False, oriented=False )
        faces     = [ int( dimtag[1] ) for dimtag in dimtags_s ]
        edges     = [ int( dimtag[1] ) for dimtag in dimtags_l ]
        fieldrest = gmsh.model.mesh.field.add( "Restrict" )
        gmsh.model.mesh.field.setNumber ( fieldrest, "IField"   , fieldmath )
        gmsh.model.mesh.field.setNumbers( fieldrest, "FacesList", faces     )
        gmsh.model.mesh.field.setNumbers( fieldrest, "EdgesList", edges     )
        regions   = [ int( dimtag[1] ) for dimtag in dimtags_v ]
        gmsh.model.mesh.field.setNumbers( fieldrest, "RegionsList", regions )
    elif ( target == "surf" ):
        dimtags_s = [(itarget,volume_num)]
        dimtags_l = gmsh.model.getBoundary( dimtags_s, combined=False, oriented=False )
        faces     = [ int( dimtag[1] ) for dimtag in dimtags_s ]
        edges     = [ int( dimtag[1] ) for dimtag in dimtags_l ]
        fieldrest = gmsh.model.mesh.field.add( "Restrict" )
        gmsh.model.mesh.field.setNumber ( fieldrest, "IField"   , fieldmath )
        gmsh.model.mesh.field.setNumbers( fieldrest, "FacesList", faces     )
        gmsh.model.mesh.field.setNumbers( fieldrest, "EdgesList", edges     )
    else:
        print( "[assign__meshsize_on_each_volume] ONLY volu & surf is implemented..." )
        sys.exit()
    return( (fieldmath, fieldrest) )



# ========================================================= #
# ===  acquire__mathEval                                === #
# ========================================================= #

def acquire__mathEval( volume_num=None, meshType=None, itarget=None, \
                       meshsize  =None, mathEval=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( volume_num is None ): sys.exit( "[acquire__mathEval] volume_num == ??? " )
    if ( meshType   is None ): sys.exit( "[acquire__mathEval] meshType   == ??? " )
    if ( itarget    is None ): sys.exit( "[acquire__mathEval] itarget    == ??? " )
    if ( meshsize   is None ): sys.exit( "[acquire__mathEval] meshsize   == ??? " )
    if ( mathEval   is None ): sys.exit( "[acquire__mathEval] mathEval   == ??? " )

    # ------------------------------------------------- #
    # --- [2] return mathEval depends on meshType   --- #
    # ------------------------------------------------- #
    if   ( meshType.lower() == "direct-math" ):
        print( "[assign__meshsize.py] direct-math mode for {0}".format( volume_num ) )
        print( "[assign__meshsize.py] mathEval :: {0}"         .format( mathEval   ) )
        # use argument mathEval
        # pass
    
    elif ( meshType.lower() == "constant" ):
        mathEval   = "{0}".format( meshsize[0] )
        
    elif ( meshType.lower() in [ "gradiant-x", "gradiant-y", "gradiant-z" ] ):
        coord      = ( re.search( r"gradiant-(.)", meshType ) ).group(1)
        icoord     = { "x":0, "y":1, "z":2 }[coord]
        bb         = gmsh.model.occ.getBoundingBox( itarget, volume_num )
        pMin,pMax  = bb[icoord], bb[icoord+3]
        grad       = ( meshsize[1] - meshsize[0] ) / ( pMax - pMin )
        mathEval   = "{0}+{1}*({2}-({3}))".format( meshsize[0], grad, coord, pMin )

    elif ( meshType.lower() in [ "gradiant-r"] ):
        if ( len( mathEval.split(",") ) == 2 ):
            rMin, rMax = ( float(val) for val in mathEval.split(",") )
        else:
            bb     = gmsh.model.occ.getBoundingBox( itarget, volume_num )
            rMin   = 0.0
            rMax   = np.max( np.abs( [ bb[0], bb[1], bb[3], bb[4] ] ) )
        r_eval     = "(({1}-sqrt(x*x+y*y))/({1}-{0}))".format( rMin, rMax )
        mathEval   = "(({1}-{0})*({2})+{0})".format( meshsize[0], meshsize[1], r_eval )
        
    elif ( meshType.lower() in [ "gradiant-rz"] ):
        if ( len( mathEval.split(",") ) == 4 ):
            rMin,rMax,zMin,zMax = ( float(val) for val in mathEval.split(",") )
        else:
            print( "[assign__meshsize.py] gradiant-rtz mode needs parameter @ evaluation" )
            print( "[assign__meshsize.py]    evaluation :: rMin,rMax,zMin,zMax" )
            sys.exit()
        r_eval     = "(({1}-sqrt(x*x+y*y))/({1}-{0}))".format( rMin, rMax )
        z_eval     = "((z-{0})/({1}-{0}))"            .format( zMin, zMax )
        mathEval   = "(({1}-{0})*(Max(({2}),({3})))+{0})"\
            .format( meshsize[0], meshsize[1], r_eval, z_eval )

    elif ( meshType.lower() in [ "gradiant-rtz"] ):
        if ( len( mathEval.split(",") ) == 4 ):
            rMin,rMax,zMin,zMax = ( float(val) for val in mathEval.split(",") )
        else:
            print( "[assign__meshsize.py] gradiant-rtz mode needs parameter @ evaluation" )
            print( "[assign__meshsize.py]    evaluation :: rMin,rMax,zMin,zMax" )
            sys.exit()
        r_eval     = "(({1}-sqrt(x*x+y*y))/({1}-{0}))".format( rMin, rMax )
        z_eval     = "((z-{0})/({1}-{0}))"            .format( zMin, zMax )
        t_eval     = "(0.5*(1.0+y/sqrt(x*x+y*y)))"
        mathEval   = "(({1}-{0})*(Max(({2}),({3}),({4})))+{0})"\
            .format( meshsize[0], meshsize[1], r_eval, z_eval, t_eval )

    return( mathEval )


# ========================================================= #
# ===  load mesh and physical number config             === #
# ========================================================= #
def load__mesh_and_phys_config( meshFile=None, physFile=None, pts={}, line={}, surf={}, volu={}, loadonly=False, \
                                ptsPhys={}, linePhys={}, surfPhys={}, voluPhys={} ):

    ptsDim, lineDim, surfDim, voluDim = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( meshFile is None ): sys.exit( "[load__mesh_and_phys_config] meshFile == ???" )
    if ( physFile is None ): sys.exit( "[load__mesh_and_phys_config] physFile == ???" )
    
    # ------------------------------------------------- #
    # --- [2] Data Load                             --- #
    # ------------------------------------------------- #
    with open( meshFile ) as f:
        meshtable = f.readlines()
    with open( physFile ) as f:
        phystable = f.readlines()

    # ------------------------------------------------- #
    # --- [3] generate Dictionary ( physical Num )  --- #
    # ------------------------------------------------- #
    ptsPhysTable  = {}
    linePhysTable = {}
    surfPhysTable = {}
    voluPhysTable = {}
    physNums      = {}
    vnames        = []

    for row in phystable:
        if ( len( row.strip() ) == 0 ):
            continue
        if ( (row.strip())[0] == "#" ):
            continue
        str_venti  = row.split()[2]
        venti_list = split__values( string=str_venti )
        venti_list = [ int( venti ) for venti in venti_list ]
        n_add      = "_{0}"
        # -------- old ------------------------------- #
        # if   ( len( venti.split("-") ) >= 2 ):
        #     ifrom = int( ( venti.split("-") )[0] )
        #     iuntl = int( ( venti.split("-") )[1] )
        #     n_add = "_{0}"
        # elif ( len( venti.split("-") ) == 1 ):
        #     ifrom = int( venti )
        #     iuntl = int( venti )
        #     n_add = ""
        # -------- old ------------------------------- #
            
        for venti in venti_list:
            
            # -- [3-1] vname, vtype, venum  -- #
            vname =        ( row.split() )[0] + n_add.format( venti )
            vtype =        ( row.split() )[1]
            vphys =        ( row.split() )[3]
            
            # -- [3-2] vtype check          -- #
            if   ( vtype.lower() == 'pts'    ):
                pts [vname]     = venti
                if ( vphys in ptsPhysTable ):
                    ( ptsPhysTable[vphys] ).append( venti )
                else:
                    ptsPhysTable[vphys] = [ venti ]
            
            elif ( vtype.lower() == 'line'   ):
                line[vname]      = venti
                if ( vphys in linePhysTable ):
                    ( linePhysTable[vphys] ).append( venti )
                else:
                    linePhysTable[vphys] = [ venti ]
                    
            elif ( vtype.lower() == 'surf'   ):
                surf[vname]      = venti
                if ( vphys in surfPhysTable ):
                    ( surfPhysTable[vphys] ).append( venti )
                else:
                    surfPhysTable[vphys] = [ venti ]
                    
            elif ( vtype.lower() == 'volu'   ):
                volu[vname]      = venti
                if ( vphys in voluPhysTable ):
                    ( voluPhysTable[vphys] ).append( venti )
                else:
                    voluPhysTable[vphys] = [ venti ]
                
            else:
                print("[ERROR] Unknown Object in load__mesh_and_phys_config :: {0}".format(physFile) )
                sys.exit()

            physNums[vname] = vphys
            vnames.append( vname )


    # ------------------------------------------------- #
    # --- [4] register physical number              --- #
    # ------------------------------------------------- #

    if ( loadonly is False ):
        for key in list(  ptsPhysTable.keys() ):
            ptsPhys[key]  = gmsh.model.addPhysicalGroup( ptsDim, ptsPhysTable[key], \
                                                         tag=int(key) )
        for key in list( linePhysTable.keys() ):
            linePhys[key] = gmsh.model.addPhysicalGroup( lineDim, linePhysTable[key], \
                                                         tag=int(key) )
        for key in list( surfPhysTable.keys() ):
            surfPhys[key] = gmsh.model.addPhysicalGroup( surfDim, surfPhysTable[key], \
                                                         tag=int(key) )
        for key in list( voluPhysTable.keys() ):
            voluPhys[key] = gmsh.model.addPhysicalGroup( voluDim, voluPhysTable[key], \
                                                         tag=int(key) )

    # ------------------------------------------------- #
    # --- [3] generate Dictionary ( mesh )          --- #
    # ------------------------------------------------- #

    physMeshTable1 = {}
    physMeshTable2 = {}
    meshTypeTable_ = {}
    mathEvalTable_ = {}

    for row in meshtable:
        if ( len( row.strip() ) == 0 ):
            continue
        if ( (row.strip())[0] == "#" ):
            continue
        # -- [3-1] vname, vtype, venum  -- #
        vname  =        ( row.split() )[0]
        vphys  =        ( row.split() )[1]
        vtype  =        ( row.split() )[2]
        vmesh1 =        ( row.split() )[3]
        vmesh2 =        ( row.split() )[4]
        veval  =        ( row.split() )[5]

        try:
            vmesh1 = float( vmesh1 )
        except ValueError:
            vmesh1 = None
        
        try:
            vmesh2 = float( vmesh2 )
        except ValueError:
            vmesh2 = None
        
        if ( not( vphys in physMeshTable1 ) ):
            physMeshTable1[vphys] = vmesh1
            physMeshTable2[vphys] = vmesh2
            meshTypeTable_[vphys] = vtype
            mathEvalTable_[vphys] = veval
        else:
            print( "[assign__meshsize.py] duplicated keys :: {0}  [ERROR] ".format( vname ) )
            sys.exit()
    meshConf_has  = set( list( physMeshTable1.keys() ) )
    physNums_has  = set( list( physNums.values() ) )
    NoMeshConstra = list( physNums_has - meshConf_has )
    NoPhysDefinit = list( meshConf_has - physNums_has )
    CommonPhysNum = list( meshConf_has & physNums_has )
    
    if ( len( NoMeshConstra ) > 0 ):
        print()
        print( "[assign__meshsize.py] No Mesh Constraints   :: {0} ".format( NoMeshConstra ) )
        print()
    if ( len( NoPhysDefinit ) > 0 ):
        print()
        print( "[assign__meshsize.py] No PhysNum Definition :: {0} ".format( NoPhysDefinit ) )
        print()
        sys.exit()

    vnames_        = [ key for key in vnames if physNums[key] in CommonPhysNum ]
    meshsizeTable1 = { key: physMeshTable1[ physNums[key] ] for key in vnames_ }
    meshsizeTable2 = { key: physMeshTable2[ physNums[key] ] for key in vnames_ }
    meshTypeTable  = { key: meshTypeTable_[ physNums[key] ] for key in vnames_ }
    mathEvalTable  = { key: mathEvalTable_[ physNums[key] ] for key in vnames_ }

    meshsizelist1  = [ value for value in list( meshsizeTable1.values() ) if value is not None ]
    meshsizelist2  = [ value for value in list( meshsizeTable2.values() ) if value is not None ]
    minMeshSize    = np.min( meshsizelist1 + meshsizelist2 )
    maxMeshSize    = np.max( meshsizelist1 + meshsizelist2 )
    
    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "pts"    :pts    , "line"    :line    , "surf"    :surf    , "volu"    :volu    , \
            "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys, \
            "meshsize1":meshsizeTable1, "meshsize2":meshsizeTable2, \
            "mathEvals":mathEvalTable , "meshTypes" :meshTypeTable,
            "minMeshSize":minMeshSize, "maxMeshSize":maxMeshSize, "keys":vnames }
    return( ret )




# ========================================================= #
# ===  split__values.py                                 === #
# ========================================================= #

def split__values( string=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( string is None ): sys.exit( "[split__values] string == ???" )

    # ------------------------------------------------- #
    # --- [2] separation                            --- #
    # ------------------------------------------------- #
    #  -- [2-1] comma separation                    --  #
    cs_list = string.split( "," )

    #  -- [2-2] hyphone separation                  --  #
    hp_list = []
    for sval in cs_list:
        spl = sval.split("-")
        if   ( len( spl ) == 1 ):
            hp_list += spl
        elif ( len( spl ) == 2 ):
            hp_list += [ str(val) for val in range( int(spl[0]), int(spl[1])+1 ) ]
        else:
            sys.exit( "[split__values.py] illegal number of hyphone '-'. " )

    #  -- [2-3] return value                        --  #
    return( hp_list )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )

    gmsh.model.occ.addBox( -0.5, -0.5, -0.5, \
                           +1.0, +1.0, +1.0 )
    gmsh.model.occ.addBox( -0.0, -0.0, -0.0, \
                           +1.0, +1.0, +1.0 )

    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # meshFile = "test/mesh.conf"
    physFile = "test/phys_only.conf"
    meshFile = "test/mesh_only.conf"
    assign__meshsize( meshFile=meshFile, physFile=physFile )
    gmsh.model.occ.synchronize()

    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()










# # ========================================================= #
# # ===  load mesh config                                 === #
# # ========================================================= #
# def load__meshconfig( meshFile=None, pts={}, line={}, surf={}, volu={}, loadonly=False, \
#                       ptsPhys={}, linePhys={}, surfPhys={}, voluPhys={} ):

#     ptsDim, lineDim, surfDim, voluDim = 0, 1, 2, 3
    
#     # ------------------------------------------------- #
#     # --- [1] Arguments                             --- #
#     # ------------------------------------------------- #
#     if ( meshFile is None ): sys.exit( "[load__meshconfig] meshFile == ???" )
    
#     # ------------------------------------------------- #
#     # --- [2] Data Load                             --- #
#     # ------------------------------------------------- #
#     with open( meshFile ) as f:
#         table = f.readlines()

#     # ------------------------------------------------- #
#     # --- [3] generate Dictionary                   --- #
#     # ------------------------------------------------- #
#     ptsPhysTable  = {}
#     linePhysTable = {}
#     surfPhysTable = {}
#     voluPhysTable = {}
#     meshsizeTable = {}
#     vnames        = []

#     for row in table:
#         if ( len( row.strip() ) == 0 ):
#             continue
#         if ( (row.strip())[0] == "#" ):
#             continue
#         # -- [3-1] vname, vtype, venum  -- #
#         vname =        ( row.split() )[0]
#         vtype =        ( row.split() )[1]
#         venti = int  ( ( row.split() )[2] )
#         vphys =        ( row.split() )[3]
#         vmesh = float( ( row.split() )[4] )

#         # -- [3-2] vtype check          -- #
#         if   ( vtype.lower() == 'pts'    ):
#             pts [vname] = venti
#             if ( vphys in ptsPhysTable ):
#                 ( ptsPhysTable[vphys] ).append( venti )
#             else:
#                 ptsPhysTable[vphys] = [ venti ]
            
#         elif ( vtype.lower() == 'line'   ):
#             line[vname] = venti
#             if ( vphys in linePhysTable ):
#                 ( linePhysTable[vphys] ).append( venti )
#             else:
#                 linePhysTable[vphys] = [ venti ]

#         elif ( vtype.lower() == 'surf'   ):
#             surf[vname] = venti
#             if ( vphys in surfPhysTable ):
#                 ( surfPhysTable[vphys] ).append( venti )
#             else:
#                 surfPhysTable[vphys] = [ venti ]
                
#         elif ( vtype.lower() == 'volu'   ):
#             volu[vname] = venti
#             if ( vphys in voluPhysTable ):
#                 ( voluPhysTable[vphys] ).append( venti )
#             else:
#                 voluPhysTable[vphys] = [ venti ]
                
#         else:
#             print("[ERROR] Unknown Object in load__meshconfig :: {0}".format(meshFile) )
#             sys.exit()

#         if ( not( vname in meshsizeTable ) ):
#             meshsizeTable[vname] = vmesh
#             vnames.append( vname )
#         else:
#             print( "[load__meshconfig] duplicated keys :: {0}  [ERROR] ".format( vname ) )
#             sys.exit()

#     meshsizelist = [ meshsizeTable[key] for key in vnames ]


#     # ------------------------------------------------- #
#     # --- [4] register physical number              --- #
#     # ------------------------------------------------- #

#     if ( loadonly is False ):
#         for key in list(  ptsPhysTable.keys() ):
#             ptsPhys[key]  = gmsh.model.addPhysicalGroup( ptsDim, ptsPhysTable[key], \
#                                                          tag=int(key) )
#         for key in list( linePhysTable.keys() ):
#             linePhys[key] = gmsh.model.addPhysicalGroup( lineDim, linePhysTable[key], \
#                                                          tag=int(key) )
#         for key in list( surfPhysTable.keys() ):
#             surfPhys[key] = gmsh.model.addPhysicalGroup( surfDim, surfPhysTable[key], \
#                                                          tag=int(key) )
#         for key in list( voluPhysTable.keys() ):
#             voluPhys[key] = gmsh.model.addPhysicalGroup( voluDim, voluPhysTable[key], \
#                                                          tag=int(key) )

#     # ------------------------------------------------- #
#     # --- [5] return                                --- #
#     # ------------------------------------------------- #
#     ret = { "pts"    :pts    , "line"    :line    , "surf"    :surf    , "volu"    :volu    , \
#             "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys, \
#             "meshsize":meshsizeTable, "keys":vnames, "meshsizelist":meshsizelist }
#     return( ret )

