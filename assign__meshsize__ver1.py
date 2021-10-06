import os, sys
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
        if ( meshFile is None ):
            sys.exit( "[assign__meshsize] give meshFile or, volumes_list & meshsize_list" )
        else:
            if ( physFile is None ):
                meshconfig    = load__meshconfig( meshFile=meshFile )
                keys          = list( ( meshconfig[target] ).keys() )
                volumes_list  = [ (meshconfig[target]    )[key] for key in keys ]
                meshsize_list = [ (meshconfig["meshsize"])[key] for key in keys ]
            else:
                meshconfig    = load__mesh_and_phys_config( meshFile=meshFile, physFile=physFile )
                keys          = list( ( meshconfig[target] ).keys() )
                volumes_list  = [ (meshconfig[target]    )[key] for key in keys ]
                meshsize_list = [ (meshconfig["meshsize"])[key] for key in keys ]

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
        print( "[assign__meshsize.py] missing            :: {0} ".format( missing      ) )
        print( "[assign__meshsize.py] aborting           :: current.geo_unrolled "       )
        gmsh.write( "current.geo_unrolled" )
        print( "[assign__meshsize.py] missing Entity Error STOP " )
        sys.exit()
    
                
    # ------------------------------------------------- #
    # --- [2] define each mesh field                --- #
    # ------------------------------------------------- #
    fieldlist = []
    for ik,ms in enumerate( meshsize_list ):
        ret = assign__meshsize_on_each_volume( volume_num=volumes_list[ik], meshsize=ms, \
                                               target=target )
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
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", np.min( meshsize_list ) )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", np.max( meshsize_list ) )
    
    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "meshsize_list":meshsize_list, "volumes_list":volumes_list, \
            "field_list":fieldlist }
    return( ret )
    

# ========================================================= #
# ===  assigne meshsize onto volume Entities            === #
# ========================================================= #
def assign__meshsize_on_each_volume( volume_num=None, meshsize=None, target="volu" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( volume_num is None ): sys.exit( "[assign__meshsize_on_each_volume] volume_num == ??? " )
    if ( meshsize   is None ): sys.exit( "[assign__meshsize_on_each_volume] meshsize   == ??? " )
    itarget   = ( ["pts","line","surf","volu"] ).index( target )
    
    # ------------------------------------------------- #
    # --- [2] define MathEval Field                 --- #
    # ------------------------------------------------- #
    fieldmath = gmsh.model.mesh.field.add( "MathEval" )
    gmsh.model.mesh.field.setString( fieldmath, "F", "{0}".format( meshsize ) )

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
# ===  load mesh config                                 === #
# ========================================================= #
def load__meshconfig( meshFile=None, pts={}, line={}, surf={}, volu={}, loadonly=False, \
                      ptsPhys={}, linePhys={}, surfPhys={}, voluPhys={} ):

    ptsDim, lineDim, surfDim, voluDim = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( meshFile is None ): sys.exit( "[load__meshconfig] meshFile == ???" )
    
    # ------------------------------------------------- #
    # --- [2] Data Load                             --- #
    # ------------------------------------------------- #
    with open( meshFile ) as f:
        table = f.readlines()

    # ------------------------------------------------- #
    # --- [3] generate Dictionary                   --- #
    # ------------------------------------------------- #
    ptsPhysTable  = {}
    linePhysTable = {}
    surfPhysTable = {}
    voluPhysTable = {}
    meshsizeTable = {}
    vnames        = []

    for row in table:
        if ( len( row.strip() ) == 0 ):
            continue
        if ( (row.strip())[0] == "#" ):
            continue
        # -- [3-1] vname, vtype, venum  -- #
        vname =        ( row.split() )[0]
        vtype =        ( row.split() )[1]
        venti = int  ( ( row.split() )[2] )
        vphys =        ( row.split() )[3]
        vmesh = float( ( row.split() )[4] )

        # -- [3-2] vtype check          -- #
        if   ( vtype.lower() == 'pts'    ):
            pts [vname] = venti
            if ( vphys in ptsPhysTable ):
                ( ptsPhysTable[vphys] ).append( venti )
            else:
                ptsPhysTable[vphys] = [ venti ]
            
        elif ( vtype.lower() == 'line'   ):
            line[vname] = venti
            if ( vphys in linePhysTable ):
                ( linePhysTable[vphys] ).append( venti )
            else:
                linePhysTable[vphys] = [ venti ]

        elif ( vtype.lower() == 'surf'   ):
            surf[vname] = venti
            if ( vphys in surfPhysTable ):
                ( surfPhysTable[vphys] ).append( venti )
            else:
                surfPhysTable[vphys] = [ venti ]
                
        elif ( vtype.lower() == 'volu'   ):
            volu[vname] = venti
            if ( vphys in voluPhysTable ):
                ( voluPhysTable[vphys] ).append( venti )
            else:
                voluPhysTable[vphys] = [ venti ]
                
        else:
            print("[ERROR] Unknown Object in load__meshconfig :: {0}".format(meshFile) )
            sys.exit()

        if ( not( vname in meshsizeTable ) ):
            meshsizeTable[vname] = vmesh
            vnames.append( vname )
        else:
            print( "[load__meshconfig] duplicated keys :: {0}  [ERROR] ".format( vname ) )
            sys.exit()

    meshsizelist = [ meshsizeTable[key] for key in vnames ]


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
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "pts"    :pts    , "line"    :line    , "surf"    :surf    , "volu"    :volu    , \
            "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys, \
            "meshsize":meshsizeTable, "keys":vnames, "meshsizelist":meshsizelist }
    return( ret )


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

    meshsizeTable = {}
    physMeshTable = {}

    for row in meshtable:
        if ( len( row.strip() ) == 0 ):
            continue
        if ( (row.strip())[0] == "#" ):
            continue
        # -- [3-1] vname, vtype, venum  -- #
        vname =        ( row.split() )[0]
        vphys =        ( row.split() )[1]
        vmesh = float( ( row.split() )[2] )

        if ( not( vphys in physMeshTable ) ):
            physMeshTable[vphys] = vmesh
        else:
            print( "[load__meshconfig] duplicated keys :: {0}  [ERROR] ".format( vname ) )
            sys.exit()
    meshConf_has  = set( list( physMeshTable.keys() ) )
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


    vnames_       = [ key for key in vnames if physNums[key] in CommonPhysNum ]
    meshsizeTable = { key: physMeshTable[ physNums[key] ] for key in vnames_ }
    meshsizelist  = [ physMeshTable[ physNums[key] ]      for key in vnames_ ]
            
    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "pts"    :pts    , "line"    :line    , "surf"    :surf    , "volu"    :volu    , \
            "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys, \
            "meshsize":meshsizeTable, "keys":vnames, "meshsizelist":meshsizelist }
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

    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.01 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.50 )

    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
