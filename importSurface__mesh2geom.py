import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  importSurface__mesh2geom                         === #
# ========================================================= #

def importSurface__mesh2geom( inpFile=None, elementType="triangle" ):

    pDim, lDim, sDim, vDim = 0, 1, 2, 3
    dim_, tag_ = 0, 1
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[importSurface__mesh2geom.py] inpFile == ???" )

    # ------------------------------------------------- #
    # --- [2] load mesh using meshio                --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.load__meshio as mio
    rmesh = mio.load__meshio( mshFile=inpFile, elementType=elementType )
    elems = rmesh["cells"]
    nodes = rmesh["points"]
    
    # ------------------------------------------------- #
    # --- [3] add surface fragments                 --- #
    # ------------------------------------------------- #
    ndigit,edigit   = len( str( nodes.shape[0] ) ), len( str( elems.shape[0] ) ), 
    nformat,eformat = "{:0"+str(ndigit)+"}", "{:0"+str(edigit)+"}", 
    nodeNumDict     = {}
    lineNumDict     = {}
    defined         = []
    for iE,elem in enumerate( elems ):
        # -- add point -- #
        pkey_stack = []
        lNum_stack = []
        for iN,node in enumerate( elem ):
            pkey = nformat.format( node )
            if ( not( pkey in nodeNumDict ) ):
                nodeNumDict[pkey] = gmsh.model.occ.addPoint( *nodes[node,:] )
            pkey_stack += [ pkey ]
        # -- add line  -- #
        for pair in [ (0,1), (1,2), (2,0) ]:
            pkey1, pkey2 = pkey_stack[pair[0]], pkey_stack[pair[1]], 
            lkey1, lkey2 = pkey1 + "-" + pkey2, pkey2 + "-" + pkey1
            if   ( ( lkey1 in lineNumDict ) ):
                lNum = lineNumDict[lkey1]    # (+1), can be ignored for occ
            elif ( ( lkey2 in lineNumDict ) ):
                lNum = lineNumDict[lkey2]    # (-1), can be ignored for occ
            else:
                lNum = gmsh.model.occ.addLine( nodeNumDict[pkey_stack[pair[0]]], \
                                               nodeNumDict[pkey_stack[pair[1]]]  )
                lineNumDict[lkey1] = lNum
            lNum_stack += [ lNum ]
        # -- add surface  -- #
        skey               = eformat.format( iE )
        lineGroup          = gmsh.model.occ.addCurveLoop( lNum_stack )
        defined           += [ ( sDim, gmsh.model.occ.addPlaneSurface( [ lineGroup ] ) ) ]

    # ------------------------------------------------- #
    # --- [4] merge :: boolean fuse fragments       --- #
    # ------------------------------------------------- #
    if ( len( defined ) < 2 ):
        print( "[importSurface__mesh2geom.py] #. of surface is {} :: no fuse operations "\
               .format( len( defined ) ) )
    else:
        defined,fmap = gmsh.model.occ.fuse( [ defined[0] ], defined[1:], \
                                            removeObject=True, removeTool=True )
    return( defined )


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
    inpFile = "msh/poleSurface_3d.msh"
    dimtags = {}
    dimtags = importSurface__mesh2geom( inpFile=inpFile )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
    gmsh.write( "msh/poleSurface_3d.stp" )

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = False         # from nkGMshRoutines/test/mesh.conf, phys.conf
    uniform_size     = 0.1
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
    gmsh.model.mesh.generate(2)
    gmsh.write( "msh/poleSurface_3d_remeshed.msh" )
    gmsh.finalize()

