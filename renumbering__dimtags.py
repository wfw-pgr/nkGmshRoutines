import os, sys, json
import numpy as np

# ========================================================= #
# ===  renumbering__dimtags                             === #
# ========================================================= #

def renumbering__dimtags( dimtags=None, dim=3, verbose=True ):

    dim_, tag_ = 0, 1

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( dimtags is None ): sys.exit( "[renumbering__dimtags.py] == ??? " )

    # ------------------------------------------------- #
    # --- [2] convert                               --- #
    # ------------------------------------------------- #
    entityNums = []
    keylists   = []
    allkeys    = dimtags.keys()
    for key in allkeys:
        for dimtag in dimtags[key]:
            entityNums += [ dimtag[tag_] ]
            keylists   += [ key ]
    sortedEnts = list( np.sort( entityNums ) )
    renumbers  = [ sortedEnts.index(iEnt)+1 for iEnt in entityNums ]

    # ------------------------------------------------- #
    # --- [3] rebuild dimtags                       --- #
    # ------------------------------------------------- #
    if ( verbose ):
        print( "\n" + "[renumbering__dimtags.py] old_dimtags ==> new_dimtags...."  + "\n" )
    ret = { key:[] for key in allkeys }
    for ik,key in enumerate( keylists ):
        ret[key] += [ (dim,renumbers[ik]) ]
        if ( verbose ):
            print( "[renumbering__dimtags.py] {0:>25} :: [({1:1d},{2:5d})] ==> [({1:1d},{3:5d})]"\
                   .format( key, dim, entityNums[ik], renumbers[ik] ) )
    return( ret )



# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #
if ( __name__=="__main__" ):
    import nkGmshRoutines.load__dimtags as ldt
    dimtags = ldt.load__dimtags( inpFile="test/dimtags.json" )
    renumed = renumbering__dimtags( dimtags=dimtags )

    print( renumed )
