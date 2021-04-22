import os, sys
import numpy         as np
# import gmsh_api.gmsh as gmsh
import gmsh

# ========================================================= #
# ===  assign mesh size ( main routine )                === #
# ========================================================= #
def assign__meshsize( meshsize_list=None, volumes_list=None, meshFile=None ):

    voluDim = 3

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    meshconfig = None
    if ( ( meshsize_list is None ) and ( volumes_list is None ) ):
        if ( meshFile is None ):
            sys.exit( "[assign__meshsize] give meshFile or, volumes_list & meshsize_list" )
        else:
            meshconfig    = load__meshconfig( meshFile=meshFile )
            keys          = list( ( meshconfig["volu"] ).keys() )
            volumes_list  = [ (meshconfig["volu"]    )[key] for key in keys ]
            meshsize_list = [ (meshconfig["meshsize"])[key] for key in keys ]

    # ------------------------------------------------- #
    # --- [2] define each mesh field                --- #
    # ------------------------------------------------- #
    fieldlist = []
    for ik,ms in enumerate( meshsize_list ):
        ret = assign__meshsize_on_each_volume( volume_num=volumes_list[ik], meshsize=ms )
        fieldlist.append( ret[1] )

    # ------------------------------------------------- #
    # --- [3] define total field                    --- #
    # ------------------------------------------------- #
    totalfield = gmsh.model.mesh.field.add( "Min" )
    gmsh.model.mesh.field.setNumbers( totalfield, "FieldsList", fieldlist )
    gmsh.model.mesh.field.setAsBackgroundMesh( totalfield )

    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #
    ret = { "meshsize_list":meshsize_list, "volumes_list":volumes_list, \
            "field_list":fieldlist }
    return( ret )
    

# ========================================================= #
# ===  assigne meshsize onto volume Entities            === #
# ========================================================= #
def assign__meshsize_on_each_volume( volume_num=None, meshsize=None ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( volume_num is None ): sys.exit( "[assign__meshsize_on_each_volume] volume_num == ??? " )
    if ( meshsize   is None ): sys.exit( "[assign__meshsize_on_each_volume] meshsize   == ??? " )
    dimtags_v = [(3,volume_num)]
    
    # ------------------------------------------------- #
    # --- [2] define MathEval Field                 --- #
    # ------------------------------------------------- #
    fieldmath = gmsh.model.mesh.field.add( "MathEval" )
    gmsh.model.mesh.field.setString( fieldmath, "F", "{0}".format( meshsize ) )

    # ------------------------------------------------- #
    # --- [3] define Restrict Field                 --- #
    # ------------------------------------------------- #
    dimtags_s = gmsh.model.getBoundary( dimtags_v )
    dimtags_l = gmsh.model.getBoundary( dimtags_s, combined=False, oriented=False )
    faces     = [ int( dimtag[1] ) for dimtag in dimtags_s ]
    edges     = [ int( dimtag[1] ) for dimtag in dimtags_l ]
    fieldrest = gmsh.model.mesh.field.add( "Restrict" )
    gmsh.model.mesh.field.setNumber ( fieldrest, "IField"   , fieldmath )
    gmsh.model.mesh.field.setNumbers( fieldrest, "FacesList", faces     )
    gmsh.model.mesh.field.setNumbers( fieldrest, "EdgesList", edges     )
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
        else:
            print( "[load__meshconfig] duplicated keys :: {0}  [ERROR] ".format( vname ) )
            sys.exit()

    keys         = list( meshsizeTable.keys() )
    meshsizelist = [ meshsizeTable[key] for key in keys ]


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
            "meshsize":meshsizeTable, "keys":keys, "meshsizelist":meshsizelist }
    return( ret )


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

    meshFile = "test/mesh.conf"
    assign__meshsize( meshFile=meshFile )
    gmsh.model.occ.synchronize()

    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.01 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.50 )

    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
