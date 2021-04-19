import sys
# import gmsh_api.gmsh as gmsh
import gmsh

# ========================================================= #
# ===  Load Physical Number Table for Gmsh              === #
# ========================================================= #
def load__physNumTable( inpFile=None, pts={}, line={}, surf={}, volu={}, \
                        ptsPhys={}, linePhys={}, surfPhys={}, voluPhys={} ):

    ptsDim, lineDim, surfDim, voluDim = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit(" [LoadConst] inpFile == ?? ")
    
    # ------------------------------------------------- #
    # --- [2] Data Load                             --- #
    # ------------------------------------------------- #
    with open( inpFile ) as f:
        table = f.readlines()
        
    # ------------------------------------------------- #
    # --- [3] generate Dictionary                   --- #
    # ------------------------------------------------- #
    ptsPhysTable  = {}
    linePhysTable = {}
    surfPhysTable = {}
    voluPhysTable = {}

    gmsh.model.occ.synchronize()

    for row in table:
        if ( len( row.strip() ) == 0 ):
            continue
        if ( ( ( row.strip() )[0] != "#" ) ):
            # -- [3-1] vname, vtype, venum  -- #
            vname =      ( row.split() )[0]
            vtype =      ( row.split() )[1]
            venti = int( ( row.split() )[2] )
            vphys =      ( row.split() )[3]
            
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
                print("[ERROR] Unknown Object in LoadConst :: {0} [ERROR]".format(inpFile) )

    # ------------------------------------------------- #
    # --- [4] register physical number              --- #
    # ------------------------------------------------- #
            
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
            "ptsPhys":ptsPhys, "linePhys":linePhys, "surfPhys":surfPhys, "voluPhys":voluPhys }
    return( ret )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    inpFile = "physNumTable.conf"
    load__physNumTable( inpFile=inpFile )
