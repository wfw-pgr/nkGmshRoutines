import os, sys, json
import numpy as np

# ========================================================= #
# ===  load__dimtags.py                                 === #
# ========================================================= #

def load__dimtags( inpFile=None, dimtags=None ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[load__dimtags.py] inpFile == ???" )

    # ------------------------------------------------- #
    # --- [2] load from a file                      --- #
    # ------------------------------------------------- #
    with open( inpFile, "r" ) as f:
        text = f.read()

    # ------------------------------------------------- #
    # --- [3] convert into dict                     --- #
    # ------------------------------------------------- #
    ret = json.loads( text )

    # ------------------------------------------------- #
    # --- [4] to tuple                              --- #
    # ------------------------------------------------- #
    for key in ret.keys():
        ret[key] = [ tuple(lst) for lst in ret[key] ]

    # ------------------------------------------------- #
    # --- [5] merge in dimtags                      --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        return( ret )
    else:
        dimtags = { **dimtags, **ret }
        return( dimtags )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    inpFile = "test/dimtags.json"
    dimtags = load__dimtags( inpFile=inpFile )
    print( dimtags )
