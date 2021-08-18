import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__splineCurve.py                             === #
# ========================================================= #

def make__splineCurve( inpFile=None, Data=None, closed=False, addSurface=False, eps=1.e-10 ):

    # ------------------------------------------------- #
    # --- [1] preparation / load data               --- #
    # ------------------------------------------------- #
    x_,y_,z_ = 0, 1, 2


    if ( Data is None ):
        if ( inpFile is None ):
            sys.exit( "[make__splineCurve.py] Data == ??? ( or  inpFile == ??? ) " )
        else:
            import nkUtilities.load__pointFile as lpf
            Data     = lpf.load__pointFile( inpFile=inpFile, returnType="point" )

    if ( addSurface ):
        closed = True
            
    # ------------------------------------------------- #
    # --- [2] make points                           --- #
    # ------------------------------------------------- #
    ptags = []
    pts   = {}
    lines = {}
    volus = {}
    surfs = {}
    for ik,pt in enumerate( Data ):
        ret       = gmsh.model.occ.addPoint( pt[x_], pt[y_], pt[z_] )
        pkey      = "pt{0}".format( ik+1 )
        pts[pkey] = ret
        ptags.append( ret )
    startpt = ptags[0]
    endpt   = ptags[-1]
    
    if ( closed ):
        if ( np.sqrt( np.sum( ( Data[0,:] - Data[-1,:] )**2 ) ) < eps ):
            pass
        else:
            ptags.append( ptags[0] )

    # ------------------------------------------------- #
    # --- [3] make spline curve                     --- #
    # ------------------------------------------------- #
    lines["spline"] = gmsh.model.occ.addSpline( ptags )

    # ------------------------------------------------- #
    # --- [4] make spline curve surface             --- #
    # ------------------------------------------------- #
    if ( addSurface ):
        lineloop        = gmsh.model.occ.addCurveLoop( [ lines["spline"] ] )
        surfs["spline"] = gmsh.model.occ.addPlaneSurface( [ lineloop ] )

    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "lines":lines, "surfs":surfs, "volus":volus, \
            "startpt":startpt, "endpt":endpt }
    return( ret )

    


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 1 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 1 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    inpFile = "dat/points.dat"
    make__splineCurve( inpFile=inpFile )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    # meshFile = "dat/mesh.conf"
    # import nkGmshRoutines.assign__meshsize as ams
    # meshes = ams.assign__meshsize( meshFile=meshFile )
    
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    

