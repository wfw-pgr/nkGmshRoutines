import os, sys
import gmsh

# ========================================================= #
# ===  boolean__fromTable                               === #
# ========================================================= #

def boolean__fromTable( inpFile="test/boolean.conf", dimtags=None, \
                        keys=None, names=None, table=None ):

    # ------------------------------------------------- #
    # --- [1] load table                            --- #
    # ------------------------------------------------- #
    if ( table   is None ):
        import nkUtilities.load__keyedTable as lkt
        table = lkt.load__keyedTable( inpFile=inpFile )
    if ( keys    is None ):
        keys  = list(   table.keys() )
    if ( names   is None ):
        names = list( ( table[keys[0]] ).keys() )
    if ( dimtags is None ):
        sys.exit( "[boolean__fromTable]  dimtags == ???" )

    # ------------------------------------------------- #
    # --- [2] boolean execution                     --- #
    # ------------------------------------------------- #
    for key in keys:
        card = table[key]

        # ------------------------------------------------- #
        # --- [2-1] boolean cut                         --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "cut"  ):
            dimtags[key] = boolean__cut ( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-2] boolean fuse                        --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "fuse" ):
            dimtags[key] = boolean__fuse( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-3] boolean intersect                   --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "intersect" ):
            dimtags[key] = boolean__intersect( card=card, dimtags=dimtags )
    
    return( dimtags )


# ========================================================= #
# ===  boolean__cut                                     === #
# ========================================================= #

def boolean__cut( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__cut] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__cut] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    if ( not( "removeObject"  in card ) ): card["removeObject"] = True
    if ( not( "removeTool"    in card ) ): card["removeTool"]   = True
    if ( card["removeObject"] is None   ): card["removeObject"] = True
    if ( card["removeTool"]   is None   ): card["removeTool"]   = True
    target    = [ dimtags[key] for key in card["targetKeys"] ]
    tool      = [ dimtags[key] for key in card["toolKeys"  ] ]
    ret,fmap  = gmsh.model.occ.cut( target, tool, \
                                    removeObject=card["removeObject"], \
                                    removeTool  =card["removeTool"]    )
    # ------------------------------------------------- #
    # --- [3] erase dimtags resistration            --- #
    # ------------------------------------------------- #
    if ( card["removeObject"] ):
        for key in card["targetKeys"]:
            dimtags.pop( key )
    if ( card["removeTool"]   ):
        for key in card["toolKeys"]:
            dimtags.pop( key )
    gmsh.model.occ.synchronize()
    return( ret )


# ========================================================= #
# ===  boolean__fuse                                    === #
# ========================================================= #

def boolean__fuse( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__fuse] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__fuse] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    if ( not( "removeObject"  in card ) ): card["removeObject"] = True
    if ( not( "removeTool"    in card ) ): card["removeTool"]   = True
    if ( card["removeObject"] is None   ): card["removeObject"] = True
    if ( card["removeTool"]   is None   ): card["removeTool"]   = True
    target    = [ dimtags[key] for key in card["targetKeys"] ]
    tool      = [ dimtags[key] for key in card["toolKeys"  ] ]
    ret,fmap  = gmsh.model.occ.fuse( target, tool, \
                                     removeObject=card["removeObject"], \
                                     removeTool  =card["removeTool"]    )
    # ------------------------------------------------- #
    # --- [3] erase dimtags resistration            --- #
    # ------------------------------------------------- #
    if ( card["removeObject"] ):
        for key in card["targetKeys"]:
            dimtags.pop( key )
    if ( card["removeTool"]   ):
        for key in card["toolKeys"]:
            dimtags.pop( key )
    gmsh.model.occ.synchronize()
    return( ret )


# ========================================================= #
# ===  boolean__intersect                               === #
# ========================================================= #

def boolean__intersect( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__intersect] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__intersect] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    if ( not( "removeObject"  in card ) ): card["removeObject"] = True
    if ( not( "removeTool"    in card ) ): card["removeTool"]   = True
    if ( card["removeObject"] is None   ): card["removeObject"] = True
    if ( card["removeTool"]   is None   ): card["removeTool"]   = True
    target    = [ dimtags[key] for key in card["targetKeys"] ]
    tool      = [ dimtags[key] for key in card["toolKeys"  ] ]
    ret,fmap  = gmsh.model.occ.intersect( target, tool, \
                                          removeObject=card["removeObject"], \
                                          removeTool  =card["removeTool"]    )
    # ------------------------------------------------- #
    # --- [3] erase dimtags resistration            --- #
    # ------------------------------------------------- #
    if ( card["removeObject"] ):
        for key in card["targetKeys"]:
            dimtags.pop( key )
    if ( card["removeTool"]   ):
        for key in card["toolKeys"]:
            dimtags.pop( key )
    gmsh.model.occ.synchronize()
    return( ret )


# ========================================================= #
# ===   Execution of Pragram                            === #
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
    import nkGmshRoutines.define__geometry as geo
    dimtags = geo.define__geometry( inpFile="test/geometry2.conf" )
    gmsh.model.occ.synchronize()
    
    boolean__fromTable  ( inpFile="test/boolean.conf", dimtags=dimtags )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    
    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
