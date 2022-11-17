import os, sys, re
import numpy         as np
import gmsh
import nkUtilities.load__keyedTable as lkt

# ========================================================= #
# ===  assign mesh size ( main routine )                === #
# ========================================================= #
def assign__meshsize( meshFile=None, physFile=None, dimtags=None, uniform=None, target="volu" ):

    dim_   , ent_    = 0, 1
    ptsDim , lineDim = 0, 1
    surfDim, voluDim = 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( uniform is not None ):
        if ( uniform == 0.0 ):
            xyzMinMax = gmsh.model.getBoundingBox( -1, -1 )
            xL        = ( xyzMinMax[3] - xyzMinMax[0] )
            yL        = ( xyzMinMax[4] - xyzMinMax[1] )
            zL        = ( xyzMinMax[5] - xyzMinMax[2] )
            typLength = np.max( np.array( [ xL, yL, zL ] ) )
            uniform   = typLength * 0.02
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", uniform )
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", uniform )
        return()
    if ( meshFile is None ): sys.exit( "[assign__meshsize.py] meshFile == ???" )
    if ( physFile is None ): sys.exit( "[assign__meshsize.py] physFile == ???" )
    if ( dimtags  is None ): sys.exit( "[assign__meshsize.py] dimtags  == ???" )
    
    # ------------------------------------------------- #
    # --- [2] obtain table & possible dimtags keys  --- #
    # ------------------------------------------------- #
    meshconfig = lkt.load__keyedTable( inpFile=meshFile )
    physconfig = lkt.load__keyedTable( inpFile=physFile )
    physKeys     = list( physconfig.keys() )
    meshKeys     = list( meshconfig.keys() )
    aldtKeys     = []
    resolveDict  = {}
    for physKey in physKeys:
        dimtags_keys_loc  = ( physconfig[physKey] )["dimtags_keys"]
        aldtKeys         += dimtags_keys_loc
        stack             = { dimtag_key:physKey for dimtag_key in dimtags_keys_loc }
        resolveDict       = { **resolveDict, **stack }

    # ------------------------------------------------- #
    # --- [3] store mesh / phys info as lists       --- #
    # ------------------------------------------------- #
    dtagKeys     = []
    entitiesList = []
    physNumsList = []
    entitiesDict = {}
    physNumsDict = {}
    for aldtKey in aldtKeys:
        if ( aldtKey in dimtags ):
            n_dimtag = len( dimtags[aldtKey] )
            if   ( n_dimtag >= 2 ):
                dtagKeys     += [ aldtKey+".{0}".format(ik+1) for ik in range( n_dimtag ) ]
                entitiesList += [ dimtag[ent_] for dimtag in dimtags[aldtKey] ]
                physNumsList += [ physconfig[ resolveDict[aldtKey] ]["physNum"] \
                                  for ik in range( n_dimtag ) ]
                for ik in range( n_dimtag ):
                    key_loc               = aldtKey+".{0}".format(ik+1)
                    resolveDict[key_loc]  = resolveDict[aldtKey]
                    entitiesDict[key_loc] = ( dimtags[aldtKey] )[ik][ent_]
                    physNumsDict[key_loc] = physconfig[ resolveDict[aldtKey] ]["physNum"]
                # resolveDict.pop( aldtKey ) # to erase old key
                
            elif ( n_dimtag == 1 ):
                dtagKeys     += [ aldtKey ]
                entitiesList += [ dimtags[aldtKey][0][ent_] ]
                physNumsList += [ physconfig[ resolveDict[aldtKey] ]["physNum"] ]
                entitiesDict[aldtKey] = dimtags[aldtKey][0][ent_]
                physNumsDict[aldtKey] = physconfig[ resolveDict[aldtKey] ]["physNum"]
            else:
                print( "[assign__meshsize.py] empty dimtags @ key = {0}".format( aldtKey ) )
                
    # ------------------------------------------------- #
    # --- [4] convert dictionary for mesh config    --- #
    # ------------------------------------------------- #
    mc           = meshconfig
    meshTypeDict = { str(mc[key]["physNum"]):mc[key]["meshType"]    for key in meshKeys }
    resolut1Dict = { str(mc[key]["physNum"]):mc[key]["resolution1"] for key in meshKeys }
    resolut2Dict = { str(mc[key]["physNum"]):mc[key]["resolution2"] for key in meshKeys }
    evaluateDict = { str(mc[key]["physNum"]):mc[key]["evaluation"]  for key in meshKeys }
    
    # ------------------------------------------------- #
    # --- [5] make physNum <=> entityNum table      --- #
    # ------------------------------------------------- #
    ptsPhys, linePhys, surfPhys, voluPhys = {}, {}, {}, {}
    for dtagKey in dtagKeys:
        physType = str( physconfig[ resolveDict[dtagKey] ]["type"]    )
        s_phys   = str( physconfig[ resolveDict[dtagKey] ]["physNum"] )
        if ( physType.lower() == "pts" ):
            if ( s_phys in  ptsPhys ):
                ptsPhys[s_phys]  += [ entitiesDict[dtagKey] ]
            else:
                ptsPhys[s_phys]   = [ entitiesDict[dtagKey] ]
        if ( physType.lower() == "line" ):
            if ( s_phys in linePhys ):
                linePhys[s_phys] += [ entitiesDict[dtagKey] ]
            else:
                linePhys[s_phys]  = [ entitiesDict[dtagKey] ]
        if ( physType.lower() == "surf" ):
            if ( s_phys in surfPhys ):
                surfPhys[s_phys] += [ entitiesDict[dtagKey] ]
            else:
                surfPhys[s_phys]  = [ entitiesDict[dtagKey] ]
        if ( physType.lower() == "volu" ):
            if ( s_phys in voluPhys ):
                voluPhys[s_phys] += [ entitiesDict[dtagKey] ]
            else:
                voluPhys[s_phys]  = [ entitiesDict[dtagKey] ]

    # ------------------------------------------------- #
    # --- [6] physical grouping                     --- #
    # ------------------------------------------------- #
    for s_phys in list(  ptsPhys.keys() ):
        gmsh.model.addPhysicalGroup(  ptsDim,  ptsPhys[str(s_phys)], tag=int(s_phys) )
    for s_phys in list( linePhys.keys() ):
        gmsh.model.addPhysicalGroup( lineDim, linePhys[str(s_phys)], tag=int(s_phys) )
    for s_phys in list( surfPhys.keys() ):
        gmsh.model.addPhysicalGroup( surfDim, surfPhys[str(s_phys)], tag=int(s_phys) )
    for s_phys in list( voluPhys.keys() ):
        gmsh.model.addPhysicalGroup( voluDim, voluPhys[str(s_phys)], tag=int(s_phys) )
        
    # ------------------------------------------------- #
    # --- [7] make list for every dimtags's keys    --- #
    # ------------------------------------------------- #
    meshTypes    = [ meshTypeDict[ str(physNum) ] for physNum in physNumsList ]
    resolute1    = [ resolut1Dict[ str(physNum) ] for physNum in physNumsList ]
    resolute2    = [ resolut2Dict[ str(physNum) ] for physNum in physNumsList ]
    mathEvals    = [ evaluateDict[ str(physNum) ] for physNum in physNumsList ]

    # ------------------------------------------------- #
    # --- [8] resolution (Min,Max) treatment        --- #
    # ------------------------------------------------- #
    resolute1    = [ None if type(val) is str else val for val in resolute1 ]
    resolute2    = [ None if type(val) is str else val for val in resolute2 ]
    minMeshSize  = min( [ val for val in resolute1 if val is not None ] + [ val for val in resolute2 if val is not None ] )
    maxMeshSize  = max( [ val for val in resolute1 if val is not None ] + [ val for val in resolute2 if val is not None ] )
    print( "[assign__meshsize.py] Min. of MeshSize   :: {0} ".format( minMeshSize ) )
    print( "[assign__meshsize.py] Max. of MeshSize   :: {0} ".format( maxMeshSize ) )
    print()
    
    # ------------------------------------------------- #
    # --- [9] check entity numbers                  --- #
    # ------------------------------------------------- #
    itarget   = ( ["pts","line","surf","volu"] ).index( target )
    allEntities = gmsh.model.getEntities(itarget)
    allEntities = [ int(dimtag[1]) for dimtag in allEntities ]
    missing     = list( set( entitiesList ) - set( allEntities  ) )
    remains     = list( set( allEntities  ) - set( entitiesList ) )
    print( "[assign__meshsize.py] listed entity nums :: {0} ".format( entitiesList ) )
    print( "[assign__meshsize.py] all Entities       :: {0} ".format( allEntities  ) )
    print( "[assign__meshsize.py] remains            :: {0} ".format( remains      ) )
    print()
    print( "[assign__meshsize.py] Mesh Configuration " )
    print( "  key :: type  min  max  mathEval" )
    for ik, physNum in enumerate(physNumsList):
        print( "  {0} :: {1}  {2}  {3}  {4}".format( physNum, meshTypes[ik], resolute1[ik], \
                                                     resolute2[ik], mathEvals[ik] ) )
    print()
    
    # ------------------------------------------------- #
    # --- [10] error message for missing entities   --- #
    # ------------------------------------------------- #
    if ( len( missing ) > 0 ):
        print( "[assign__meshsize.py] missing            :: {0} ".format( missing  ) )
        print( "[assign__meshsize.py] aborting, saving   :: current.msh "       )
        gmsh.option.setNumber( "General.Verbosity"           ,           3 )
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", minMeshSize )
        gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", maxMeshSize )
        gmsh.model.mesh.generate(3)
        gmsh.write( "current.msh" )
        print( "[assign__meshsize.py] missing Entity Error STOP " )
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [11] error message for remains entities   --- #
    # ------------------------------------------------- #
    if ( len( remains ) > 0 ):
        print( "[assign__meshsize.py] remains            :: {0}  ".format( remains  ) )
        print( "[assign__meshsize.py] generate uniform mesh ??? >> (y/n)", end="" )
        typing = ( ( input() ).strip() ).lower()
        if ( typing == "y" ):
            gmsh.option.setNumber( "General.Verbosity"           ,           3 )
            gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", minMeshSize )
            gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", maxMeshSize )
            gmsh.model.mesh.generate(3)
            gmsh.write( "current.msh" )
        print( "[assign__meshsize.py] continue ???              >> (y/n)", end="" )
        typing = ( ( input() ).strip() ).lower()
        if ( typing == "y" ):
            pass
        else:
            print( "[assign__meshsize.py] remains Entity Error STOP " )
            sys.exit()
                
    # ------------------------------------------------- #
    # --- [12] define each mesh field               --- #
    # ------------------------------------------------- #
    fieldlist = []
    for ik,vl in enumerate( entitiesList ):
        ms  = [ resolute1[ik], resolute2[ik] ]
        ret = assign__meshsize_on_each_volume( volume_num=vl, meshsize=ms, target=target, \
                                               meshType  =meshTypes[ik], \
                                               mathEval  =mathEvals[ik] )
        fieldlist.append( ret[1] )

    # ------------------------------------------------- #
    # --- [13] define total field                   --- #
    # ------------------------------------------------- #
    totalfield = gmsh.model.mesh.field.add( "Min" )
    gmsh.model.mesh.field.setNumbers( totalfield, "FieldsList", fieldlist )
    gmsh.model.mesh.field.setAsBackgroundMesh( totalfield )

    # ------------------------------------------------- #
    # --- [14] define Min Max size                  --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", minMeshSize )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", maxMeshSize )
    
    # ------------------------------------------------- #
    # --- [15] return                               --- #
    # ------------------------------------------------- #
    ret = { "meshsize_list":resolute1, "entitiesList":entitiesList, \
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
            rMin, rMax         = ( float(val) for val in mathEval.split(",") )
            xc  , yc           = 0.0, 0.0
        if ( len( mathEval.split(",") ) == 4 ):
            rMin, rMax, xc, yc = ( float(val) for val in mathEval.split(",") )
        else:
            bb                 = gmsh.model.occ.getBoundingBox( itarget, volume_num )
            rMax               = np.max( np.abs( [ bb[0], bb[1], bb[3], bb[4] ] ) )
            xc  , yc , rMin    = 0.0, 0.0, 0.0
        r_eval     = "(({1}-sqrt((x-({2}))^2+(y-({3}))^2))/({1}-{0}))"\
            .format( rMin, rMax, xc, yc )
        mathEval   = "(({1}-{0})*({2})+{0})".format( meshsize[0], meshsize[1], r_eval )
        
    elif ( meshType.lower() in [ "gradiant-rz"] ):
        if   ( len( mathEval.split(",") ) == 4 ):
            rMin,rMax,zMin,zMax       = ( float(val) for val in mathEval.split(",") )
            xc, yc                    = 0.0, 0.0
        elif ( len( mathEval.split(",") ) == 6 ):
            rMin,rMax,zMin,zMax,xc,yc = ( float(val) for val in mathEval.split(",") )
        else:
            print( "[assign__meshsize.py] gradiant-rtz mode needs parameter @ evaluation" )
            print( "[assign__meshsize.py]    evaluation :: rMin,rMax,zMin,zMax" )
            sys.exit()
        r_eval     = "(({1}-sqrt((x-({2}))^2+(y-({3}))^2))/({1}-{0}))"\
            .format( rMin, rMax, xc, yc )
        z_eval     = "((z-{0})/({1}-{0}))"            .format( zMin, zMax )
        mathEval   = "(({1}-{0})*(Max(({2}),({3})))+{0})"\
            .format( meshsize[0], meshsize[1], r_eval, z_eval )

    elif ( meshType.lower() in [ "gradiant-rtz"] ):
        if ( len( mathEval.split(",") ) == 4 ):
            rMin,rMax,zMin,zMax       = ( float(val) for val in mathEval.split(",") )
            xc, yc                    = 0.0, 0.0
        elif ( len( mathEval.split(",") ) == 6 ):
            rMin,rMax,zMin,zMax,xc,yc = ( float(val) for val in mathEval.split(",") )
        else:
            print( "[assign__meshsize.py] gradiant-rtz mode needs parameter @ evaluation" )
            print( "[assign__meshsize.py]    evaluation :: rMin,rMax,zMin,zMax" )
            sys.exit()
        r_eval     = "(({1}-sqrt((x-({2}))^2+(y-({3}))^2))/({1}-{0}))"\
            .format( rMin, rMax, xc, yc )
        z_eval     = "((z-{0})/({1}-{0}))"            .format( zMin, zMax )
        t_eval     = "(0.5*(1.0+y/sqrt(x*x+y*y)))"
        mathEval   = "(({1}-{0})*(Max(({2}),({3}),({4})))+{0})"\
            .format( meshsize[0], meshsize[1], r_eval, z_eval, t_eval )

    debug = True
    if ( debug ):
        print( mathEval )
        
    return( mathEval )


# # ========================================================= #
# # ===  load mesh and physical number config             === #
# # ========================================================= #
# def load__mesh_and_phys_config( meshFile=None, physFile=None, pts={}, line={}, surf={}, volu={}, loadonly=False, \
#                                 ptsPhys={}, linePhys={}, surfPhys={}, voluPhys={} ):

#     ptsDim, lineDim, surfDim, voluDim = 0, 1, 2, 3
    
#     # ------------------------------------------------- #
#     # --- [1] Arguments                             --- #
#     # ------------------------------------------------- #
#     if ( meshFile is None ): sys.exit( "[load__mesh_and_phys_config] meshFile == ???" )
#     if ( physFile is None ): sys.exit( "[load__mesh_and_phys_config] physFile == ???" )
    
#     # ------------------------------------------------- #
#     # --- [2] Data Load                             --- #
#     # ------------------------------------------------- #
#     with open( meshFile ) as f:
#         meshtable = f.readlines()
#     with open( physFile ) as f:
#         phystable = f.readlines()

#     # ------------------------------------------------- #
#     # --- [3] generate Dictionary ( physical Num )  --- #
#     # ------------------------------------------------- #
#     ptsPhysTable  = {}
#     linePhysTable = {}
#     surfPhysTable = {}
#     voluPhysTable = {}
#     physNums      = {}
#     vnames        = []

#     for row in phystable:
#         if ( len( row.strip() ) == 0 ):
#             continue
#         if ( (row.strip())[0] == "#" ):
#             continue
#         str_venti  = row.split()[2]
#         venti_list = split__values( string=str_venti )
#         venti_list = [ int( venti ) for venti in venti_list ]
#         n_add      = "_{0}"
#         # -------- old ------------------------------- #
#         # if   ( len( venti.split("-") ) >= 2 ):
#         #     ifrom = int( ( venti.split("-") )[0] )
#         #     iuntl = int( ( venti.split("-") )[1] )
#         #     n_add = "_{0}"
#         # elif ( len( venti.split("-") ) == 1 ):
#         #     ifrom = int( venti )
#         #     iuntl = int( venti )
#         #     n_add = ""
#         # -------- old ------------------------------- #
            
#         for venti in venti_list:
            
#             # -- [3-1] vname, vtype, venum  -- #
#             vname =        ( row.split() )[0] + n_add.format( venti )
#             vtype =        ( row.split() )[1]
#             vphys =        ( row.split() )[3]
            
#             # -- [3-2] vtype check          -- #
#             if   ( vtype.lower() == 'pts'    ):
#                 pts [vname]     = venti
#                 if ( vphys in ptsPhysTable ):
#                     ( ptsPhysTable[vphys] ).append( venti )
#                 else:
#                     ptsPhysTable[vphys] = [ venti ]
            
#             elif ( vtype.lower() == 'line'   ):
#                 line[vname]      = venti
#                 if ( vphys in linePhysTable ):
#                     ( linePhysTable[vphys] ).append( venti )
#                 else:
#                     linePhysTable[vphys] = [ venti ]
                    
#             elif ( vtype.lower() == 'surf'   ):
#                 surf[vname]      = venti
#                 if ( vphys in surfPhysTable ):
#                     ( surfPhysTable[vphys] ).append( venti )
#                 else:
#                     surfPhysTable[vphys] = [ venti ]
                    
#             elif ( vtype.lower() == 'volu'   ):
#                 volu[vname]      = venti
#                 if ( vphys in voluPhysTable ):
#                     ( voluPhysTable[vphys] ).append( venti )
#                 else:
#                     voluPhysTable[vphys] = [ venti ]
                
#             else:
#                 print("[ERROR] Unknown Object in load__mesh_and_phys_config :: {0}".format(physFile) )
#                 sys.exit()

#             physNums[vname] = vphys
#             vnames.append( vname )


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
#     # --- [3] generate Dictionary ( mesh )          --- #
#     # ------------------------------------------------- #

#     physMeshTable1 = {}
#     physMeshTable2 = {}
#     meshTypeTable_ = {}
#     mathEvalTable_ = {}

#     for row in meshtable:
#         if ( len( row.strip() ) == 0 ):
#             continue
#         if ( (row.strip())[0] == "#" ):
#             continue
#         # -- [3-1] vname, vtype, venum  -- #
#         vname  =        ( row.split() )[0]
#         vphys  =        ( row.split() )[1]
#         vtype  =        ( row.split() )[2]
#         vmesh1 =        ( row.split() )[3]
#         vmesh2 =        ( row.split() )[4]
#         veval  =        ( row.split() )[5]

#         try:
#             vmesh1 = float( vmesh1 )
#         except ValueError:
#             vmesh1 = None
        
#         try:
#             vmesh2 = float( vmesh2 )
#         except ValueError:
#             vmesh2 = None
        
#         if ( not( vphys in physMeshTable1 ) ):
#             physMeshTable1[vphys] = vmesh1
#             physMeshTable2[vphys] = vmesh2
#             meshTypeTable_[vphys] = vtype
#             mathEvalTable_[vphys] = veval
#         else:
#             print( "[assign__meshsize.py] duplicated keys :: {0}  [ERROR] ".format( vname ) )
#             sys.exit()
#     meshConf_has  = set( list( physMeshTable1.keys() ) )
#     physNums_has  = set( list( physNums.values() ) )
#     NoMeshConstra = list( physNums_has - meshConf_has )
#     NoPhysDefinit = list( meshConf_has - physNums_has )
#     CommonPhysNum = list( meshConf_has & physNums_has )
    
#     if ( len( NoMeshConstra ) > 0 ):
#         print()
#         print( "[assign__meshsize.py] No Mesh Constraints   :: {0} ".format( NoMeshConstra ) )
#         print()
#     if ( len( NoPhysDefinit ) > 0 ):
#         print()
#         print( "[assign__meshsize.py] No PhysNum Definition :: {0} ".format( NoPhysDefinit ) )
#         print()
#         sys.exit()

#     vnames_        = [ key for key in vnames if physNums[key] in CommonPhysNum ]
#     meshsizeTable1 = { key: physMeshTable1[ physNums[key] ] for key in vnames_ }
#     meshsizeTable2 = { key: physMeshTable2[ physNums[key] ] for key in vnames_ }
#     meshTypeTable  = { key: meshTypeTable_[ physNums[key] ] for key in vnames_ }
#     mathEvalTable  = { key: mathEvalTable_[ physNums[key] ] for key in vnames_ }

#     meshsizelist1  = [ value for value in list( meshsizeTable1.values() ) if value is not None ]
#     meshsizelist2  = [ value for value in list( meshsizeTable2.values() ) if value is not None ]
#     minMeshSize    = np.min( meshsizelist1 + meshsizelist2 )
#     maxMeshSize    = np.max( meshsizelist1 + meshsizelist2 )
    
#     # ------------------------------------------------- #
#     # --- [5] return                                --- #
#     # ------------------------------------------------- #
#     ret = { "pts"    :pts    , "line"    :line    , "surf"    :surf    , "volu"    :volu    , \
#             "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys, \
#             "meshsize1":meshsizeTable1, "meshsize2":meshsizeTable2, \
#             "mathEvals":mathEvalTable , "meshTypes" :meshTypeTable,
#             "minMeshSize":minMeshSize, "maxMeshSize":maxMeshSize, "keys":vnames }
#     return( ret )




# # ========================================================= #
# # ===  split__values.py                                 === #
# # ========================================================= #

# def split__values( string=None ):

#     # ------------------------------------------------- #
#     # --- [1] arguments                             --- #
#     # ------------------------------------------------- #
#     if ( string is None ): sys.exit( "[split__values] string == ???" )

#     # ------------------------------------------------- #
#     # --- [2] separation                            --- #
#     # ------------------------------------------------- #
#     #  -- [2-1] comma separation                    --  #
#     cs_list = string.split( "," )

#     #  -- [2-2] hyphone separation                  --  #
#     hp_list = []
#     for sval in cs_list:
#         spl = sval.split("-")
#         if   ( len( spl ) == 1 ):
#             hp_list += spl
#         elif ( len( spl ) == 2 ):
#             hp_list += [ str(val) for val in range( int(spl[0]), int(spl[1])+1 ) ]
#         else:
#             sys.exit( "[split__values.py] illegal number of hyphone '-'. " )

#     #  -- [2-3] return value                        --  #
#     return( hp_list )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )

    
    target = "volu"

    if   ( target == "volu" ):
        physFile = "test/phys.conf"
        meshFile = "test/mesh.conf"
        gmsh.model.occ.addBox( -0.5, -0.5, -0.5, \
                               +1.0, +1.0, +1.0 )
        gmsh.model.occ.addBox( -0.0, -0.0, -0.0, \
                               +1.0, +1.0, +1.0 )
    elif ( target == "surf" ):
        physFile = "test/phys_2d.conf"
        meshFile = "test/mesh_2d.conf"
        circle1 = gmsh.model.occ.addCircle( 0.,  0.0, 0., 1.0 )
        circle2 = gmsh.model.occ.addCircle( 0., -0.4, 0., 0.4 )
        circle3 = gmsh.model.occ.addCircle( 0., -0.7, 0., 0.1 )
        cloop1  = gmsh.model.occ.addCurveLoop( [circle1] )
        cloop2  = gmsh.model.occ.addCurveLoop( [circle2] )
        cloop3  = gmsh.model.occ.addCurveLoop( [circle3] )
        surf1   = gmsh.model.occ.addPlaneSurface( [cloop1] )
        surf2   = gmsh.model.occ.addPlaneSurface( [cloop2] )
        surf3   = gmsh.model.occ.addPlaneSurface( [cloop3] )
        
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    dimtags = { "cube01":[(3,1)], "cube02":[(3,2)], "cube03":[(3,3)] }
    
    assign__meshsize( dimtags=dimtags, meshFile=meshFile, physFile=physFile, target=target )
    gmsh.model.occ.synchronize()

    if   ( target == "volu" ):
        gmsh.model.mesh.generate(3)
    elif ( target == "surf" ):
        gmsh.model.mesh.generate(2)
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

