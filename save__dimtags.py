import os, sys, json
import numpy as np

# ========================================================= #
# ===  save__dimtags.py                                 === #
# ========================================================= #

def save__dimtags( dimtags=None, outFile="dimtags.json" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( dimtags is None ): sys.exit( "[save__dimtags.py] dimtags == ???" )
    
    # ------------------------------------------------- #
    # --- [2] convert into dict                     --- #
    # ------------------------------------------------- #
    dumps = json.dumps( dimtags )

    # ------------------------------------------------- #
    # --- [3] save in a file                        --- #
    # ------------------------------------------------- #
    with open( outFile, "w" ) as f:
        f.write( dumps )
    return( dumps )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    dimtags = { "main":[(3,1),(3,2)], "sub":[(3,3),], "optional":[(3,5),(3,6),(3,9)] }
    outFile = "test/dimtags.json"
    save__dimtags( outFile=outFile, dimtags=dimtags )
