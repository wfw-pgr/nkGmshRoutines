import os, sys
import gmsh

# ========================================================= #
# ===  boolean__fromTable                               === #
# ========================================================= #

def boolean__fromTable( inpFile="test/boolean.conf", dimtags=None, \
                        keys=None, names=None, table=None ):

    boolean_types = [ "cut", "fuse", "intersect", "copy", "mirror", "symmetrize", \
                      "remove", "duplicates", "regroup", "rename", "synchronize" ]
    
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
        dimtags = {}
        
    # ------------------------------------------------- #
    # --- [2] boolean execution                     --- #
    # ------------------------------------------------- #
    for key in keys:
        card = table[key]

        # ------------------------------------------------- #
        # --- [2-1] boolean cut                         --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "cut"  ):
            dimtags[key] = boolean__cut   ( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-2] boolean fuse                        --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "fuse" ):
            dimtags[key] = boolean__fuse  ( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-3] boolean intersect                   --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "intersect" ):
            dimtags[key] = boolean__intersect( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-4] boolean copy                        --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "copy" ):
            dimtags[key] = boolean__copy  ( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-5] boolean copy                        --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() in ["mirror","symmetrize"] ):
            dimtags[key] = boolean__mirror( card=card, dimtags=dimtags )
            if ( dimtags[key] is None ): dimtags.pop( key )
        # ------------------------------------------------- #
        # --- [2-6] boolean remove                      --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "remove" ):
            removed      = boolean__remove( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-6] remove all duplicates               --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "duplicates" ):
            gmsh.model.occ.removeAllDuplicates()
            gmsh.model.occ.synchronize()
        # ------------------------------------------------- #
        # --- [2-7] regroup dimtags                     --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() in ["regroup","rename"] ):
            dimtags[key] = regroup__dimtags( card=card, dimtags=dimtags )
        # ------------------------------------------------- #
        # --- [2-8] just synchronize                    --- #
        # ------------------------------------------------- #
        if ( card["boolean_type"].lower() == "synchronize" ):
            gmsh.model.occ.synchronize()
            print( "synchronized" )
        # ------------------------------------------------- #
        # --- [2-a] debug display                       --- #
        # ------------------------------------------------- #
        if ( "debug" in card ):
            if ( card["debug"] is True ):
                entities = gmsh.model.getEntities(3)
                print()
                print( "key        :: ", key )
                print( "dimtags    :: ", dimtags )
                print( "entities   :: ", entities )
                print()
        # ------------------------------------------------- #
        # --- [2-x] exception                           --- #
        # ------------------------------------------------- #
        if ( not( card["boolean_type"].lower() in boolean_types ) ):
            print( "[boolean__fromTable.py] unknown boolean_type :: {0} "\
                   .format( card["boolean_type"] ) )
            sys.exit()
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
    if ( not( "removeObject"  in card ) ): card["removeObject"] = None
    if ( not( "removeTool"    in card ) ): card["removeTool"]   = None
    if ( card["removeObject"] is None   ): card["removeObject"] = True
    if ( card["removeTool"]   is None   ): card["removeTool"]   = False
    target, tool = [], []
    for key in card["targetKeys"]:
        target  += dimtags[key]
    for key in card["toolKeys"]:
        tool    += dimtags[key]
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
    # ------------------------------------------------- #
    # --- [4] debug displaying                      --- #
    # ------------------------------------------------- #
    if ( "debug" in card ):
        if ( card["debug"] is True ):
            print()
            print( "targetKeys :: ", card["targetKeys"] )
            print( "toolKeys   :: ", card["toolKeys"] )
            print( "target     :: ", target )
            print( "tool       :: ", tool   )
            print( "ret        :: ", ret    )
            print( "fmap       :: ", fmap   )
            print()
    return( ret )


# ========================================================= #
# ===  boolean__fuse                                    === #
# ========================================================= #

def boolean__fuse( dimtags=None, card=None, macOS=True ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__fuse] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__fuse] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    if ( not( "removeObject"  in card ) ): card["removeObject"] = None
    if ( not( "removeTool"    in card ) ): card["removeTool"]   = None
    if ( card["removeObject"] is None   ): card["removeObject"] = True
    if ( card["removeTool"]   is None   ): card["removeTool"]   = True
    target, tool = [], []
    for key in card["targetKeys"]:
        target  += dimtags[key]
    for key in card["toolKeys"]:
        tool    += dimtags[key]
    ret,fmap  = gmsh.model.occ.fuse( target, tool, \
                                     removeObject=card["removeObject"], \
                                     removeTool  =card["removeTool"]    )
    # if ( macOS ):
    #     # fuse's remove Function is mulfunctioning !!!!!
    #     dims = ret[0][0]
    #     ents = set( [ int(tag[1]) for tag in ret    ] )
    #     arg1 = set( [ int(tag[1]) for tag in target ] )
    #     arg2 = set( [ int(tag[1]) for tag in tool   ] )
    #     ents = set( ents ) - set( arg1 ) - set(arg2)
    #     ret  = [ (dims,ent) for ent in ents ]

    #     if ( card["removeObject"] ):
    #         gmsh.model.occ.remove( target )
    #     if ( card["removeTool"] ):
    #         gmsh.model.occ.remove( tool   )
        

    # ------------------------------------------------- #
    # --- [3] erase dimtags resistration            --- #
    # ------------------------------------------------- #
    if ( card["removeObject"] ):
        for key in card["targetKeys"]:
            dimtags.pop( key )
    if ( card["removeTool"]   ):
        for key in card["toolKeys"]:
            dimtags.pop( key )
    # ------------------------------------------------- #
    # --- [4] debug displaying                      --- #
    # ------------------------------------------------- #
    if ( "debug" in card ):
        if ( card["debug"] is True ):
            print()
            print( "targetKeys :: ", card["targetKeys"] )
            print( "toolKeys   :: ", card["toolKeys"] )
            print( "target     :: ", target )
            print( "tool       :: ", tool   )
            print( "ret        :: ", ret    )
            print( "fmap       :: ", fmap   )
            print()
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
    target, tool = [], []
    for key in card["targetKeys"]:
        target  += dimtags[key]
    for key in card["toolKeys"]:
        tool    += dimtags[key]
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
    # ------------------------------------------------- #
    # --- [4] debug displaying                      --- #
    # ------------------------------------------------- #
    if ( "debug" in card ):
        if ( card["debug"] is True ):
            print()
            print( "targetKeys :: ", card["targetKeys"] )
            print( "toolKeys   :: ", card["toolKeys"] )
            print( "target     :: ", target )
            print( "tool       :: ", tool   )
            print( "ret        :: ", ret    )
            print( "fmap       :: ", fmap   )
            print()
    return( ret )



# ========================================================= #
# ===  boolean__copy                                    === #
# ========================================================= #

def boolean__copy( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__copy] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__copy] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] copy target object                    --- #
    # ------------------------------------------------- #
    target      = []
    for key in card["targetKeys"]:
        target += dimtags[key]
    ret         = gmsh.model.occ.copy( target )
    # ------------------------------------------------- #
    # --- [3] debug displaying                      --- #
    # ------------------------------------------------- #
    if ( "debug" in card ):
        if ( card["debug"] is True ):
            print()
            print( "targetKeys :: ", card["targetKeys"] )
            print( "target     :: ", target )
            print( "ret        :: ", ret    )
            print( "fmap       :: "         )
            print()
    return( ret )



# ========================================================= #
# ===  boolean__remove                                  === #
# ========================================================= #

def boolean__remove( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__remove] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__remove] dimtags == ???" )
    
    if ( not( "recursive" in card ) ):
        card["recursive"] = False
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    target      = []
    for key in card["targetKeys"]:
        target += dimtags[key]
    ret         = gmsh.model.occ.remove( target, recursive=card["recursive"] )
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] rename                                --- #
    # ------------------------------------------------- #
    for key in card["targetKeys"]:
        rm = dimtags.pop( key )
    return( ret )



# ========================================================= #
# ===  boolean__mirror                                  === #
# ========================================================= #

def boolean__mirror( dimtags=None, card=None ):

    # boolean_type:"mirror", targetKeys:["item01","item02",...],
    # plane: "x-z", "x-y", etc. rename: True / False
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[boolean__mirror] card    == ???" )
    if ( dimtags is None ): sys.exit( "[boolean__mirror] dimtags == ???" )

    if ( "plane" in card  ):
        if   ( card["plane"].lower() in ["y-z", "z-y"] ):
            card["coef"] = [ 1, 0, 0, 0 ]
        elif ( card["plane"].lower() in ["x-z", "z-x"] ):
            card["coef"] = [ 0, 1, 0, 0 ]
        elif ( card["plane"].lower() in ["x-y", "y-x"] ):
            card["coef"] = [ 0, 0, 1, 0 ]
        else:
            print( "[boolean__fromTable.py] unknown mirrorPlane... {} " )
            
    if ( not( "coef" in card ) ):
        print("[boolean__mirror] cannot find coef / plane in card...  [ERROR]")
        print("[boolean__mirror] plane = [ x-y, x-z, y-z, etc. ]" )
        print("[boolean__mirror] coef  = [ a,b,c,d ] for ax+by+cz+d=0 :: plane of mirroring. ")
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [2] mirror object                         --- #
    # ------------------------------------------------- #
    target      = []
    for key in card["targetKeys"]:
        target += dimtags[key]
    if ( "mirror" in dir( gmsh.model.occ ) ):
        ret     = gmsh.model.occ.mirror    ( target, card["coef"][0], card["coef"][1], \
                                             card["coef"][2], card["coef"][3] )
    else:
        ret     = gmsh.model.occ.symmetrize( target, card["coef"][0], card["coef"][1], \
                                             card["coef"][2], card["coef"][3] )
        # symmetrize will be dprecated in the future.
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] rename                                --- #
    # ------------------------------------------------- #
    if ( "rename" in card ):
        if ( card["rename"] is True ):
            ret = target
            for key in card["targetKeys"]:
                rm = dimtags.pop( key )
    return( ret )


# ========================================================= #
# ===  regroup dimtags                                  === #
# ========================================================= #

def regroup__dimtags( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[regroup__dimtags] card    == ???" )
    if ( dimtags is None ): sys.exit( "[regroup__dimtags] dimtags == ???" )

    # ------------------------------------------------- #
    # --- [2] regroup object                        --- #
    # ------------------------------------------------- #
    ret      = []
    for key in card["targetKeys"]:
        ret += dimtags.pop( key )
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
