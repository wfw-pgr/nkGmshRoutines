import gmsh_api.gmsh as gmsh

# ========================================================= #
# ===  define__physNum_inBoundingBox                    === #
# ========================================================= #

def define__physNum_inBoundingBox( pt1=None, pt2=None, dim=None, physNum=None, eps=None, physGroup=True ):

    if ( pt1     is None ): sys.exit( "[search__entityNum] pt1     == ???" )
    if ( pt2     is None ): sys.exit( "[search__entityNum] pt2     == ???" )
    if ( dim     is None ): sys.exit( "[search__entityNum] dim     == ???" )
    if ( physNum is None ): sys.exit( "[search__entityNum] physNum == ???" )
    if ( eps is not None ):
        pt1 = [ pt1[0]-eps, pt1[1]-eps, pt1[2]-eps ]
        pt2 = [ pt2[0]+eps, pt2[1]+eps, pt2[2]+eps ]
    
    tags   = gmsh.model.getEntitiesInBoundingBox( pt1[0], pt1[1], pt1[2], pt2[0], pt2[1], pt2[2], dim=dim )
    nums   = []
    for tag in tags:
        nums.append( tag[1] )
    if ( physGroup ):
        ret = gmsh.model.addPhysicalGroup( dim, nums, tag=physNum )
    else:
        ret = nums

    return( ret )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    define__physNum_inBoundingBox()
