import os, sys, re
import numpy       as np
import gmsh
# import gmsh_api.gmsh as gmsh


# ========================================================= #
# ===  assign compound entities                         === #
# ========================================================= #
def assign__compound( compFile=None, target="volu" ):

    lineDim, surfDim, voluDim = 1, 2, 3
    
    import nkUtilities.load__configtable as lct
    config = lct.load__configtable( inpFile=compFile, returnType="list-dict" )
    
    if ( target.lower() == "volu" ):

        for cfg in config:
            if ( cfg["entityType"].lower() == "volu" ):
                entityNums = cfg["entityNum"]

                # -- investigate surf / line entity num. -- #
                volu_dimtags = [(voluDim,iV   ) for iV in entityNums ]
                surf_dimtags = gmsh.model.getBoundary( volu_dimtags, combined=True )
                line_dimtags = gmsh.model.getBoundary( surf_dimtags, combined=True, \
                                                       oriented=True )
                # compound line
                tags         = [ dimtag[1] for dimtag in line_dimtags ]
                gmsh.model.mesh.setCompound( lineDim, tags )
                # compound surface
                tags         = [ dimtag[1] for dimtag in surf_dimtags ]
                gmsh.model.mesh.setCompound( surfDim, tags )
                # compound volume
                tags         = [ dimtag[1] for dimtag in volu_dimtags ]
                gmsh.model.mesh.setCompound( voluDim, tags )
    
    return()


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

    # inpFile = "msh/some_example.stp"
    # gmsh.model.occ.importShapes( inpFile )
    # gmsh.model.occ.synchronize()
    import nkGmshRoutines.generate__hexahedron as ghh
    vertex = [ [ 0.1, 0,   0.1],
               [ 0  , 1  , 0.2],
               [ 0  , 0.1, 1.1],
               [ 0.1, 1  , 2.1],
               [ 1.1, 0  , 0.1],
               [ 0.9, 1  , 0.0],
               [ 1  , 0  , 1.0],
               [ 1.1, 1.1, 1.0] ]
    ghh.generate__hexahedron( vertex=vertex )
    gmsh.model.occ.synchronize()
    
    compFile = "dat/compound.conf"
    assign__compound( compFile=compFile )
    
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    # meshFile = "dat/mesh.conf"
    # physFile = "dat/phys.conf"
    # import nkGmshRoutines.assign__meshsize as ams
    # meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.05 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.05 )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    
