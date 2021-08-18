import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__regionAlongLine.py                         === #
# ========================================================= #

def make__regionAlongLine( Data=None, inpFile=None, upper_margin=0.10, lower_margin=0.15 ):

    x_,y_,z_ = 0, 1, 2

    # ------------------------------------------------- #
    # --- [1] preparation / load data               --- #
    # ------------------------------------------------- #
    if ( Data is None ):
        if ( inpFile is None ):
            sys.exit( "[make__splineCurve.py] Data == ??? ( or  inpFile == ??? ) " )
        else:
            import nkUtilities.load__pointFile as lpf
            Data     = lpf.load__pointFile( inpFile=inpFile, returnType="point" )

    # ------------------------------------------------- #
    # --- [2] generate tangent & normal vector      --- #
    # ------------------------------------------------- #
    ds       = np.diff( Data, axis=0 )
    ds       = np.insert( ds, -1, ds[-1,:], axis=0 )
    ds_norm  = np.sqrt( np.sum( ds**2, axis=1 ) )
    ds_norm  = np.repeat( ds_norm[:,None], 3, axis=1 )
    ds_norm  = ds / ds_norm
    dn       = np.zeros_like( ds_norm )
    dn[:,x_] =   ds_norm[:,y_]
    dn[:,y_] = - ds_norm[:,x_]
    dn[:,z_] =   ds_norm[:,z_]
    
    # ------------------------------------------------- #
    # --- [3] upper / lower line                    --- #
    # ------------------------------------------------- #
    uLine    = Data + dn*upper_margin
    lLine    = Data - dn*lower_margin
    lLine    = lLine[::-1,:]  # reverse curve points

    # ------------------------------------------------- #
    # --- [4] make spline curve in gmsh             --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.make__splineCurve as msc
    ret_u = msc.make__splineCurve( Data=uLine, addSurface=False )
    ret_l = msc.make__splineCurve( Data=lLine, addSurface=False )
    p1,p2 = ret_u["startpt"], ret_u["endpt"]
    p3,p4 = ret_l["startpt"], ret_l["endpt"]
    ul    = ( ret_u["lines"] )["spline"]
    ll    = ( ret_l["lines"] )["spline"]
    edge1 = gmsh.model.occ.addLine( p2, p3 )
    edge2 = gmsh.model.occ.addLine( p4, p1 )
    
    # ------------------------------------------------- #
    # --- [5] generate surface                      --- #
    # ------------------------------------------------- #
    lineloop = [ ul, edge1, ll, edge2 ]
    lineloop = gmsh.model.occ.addCurveLoop( lineloop )
    surf     = gmsh.model.occ.addPlaneSurface( [lineloop] )

    # ------------------------------------------------- #
    # --- [6] return                                --- #
    # ------------------------------------------------- #
    keys_u   = list( ret_u["pts"].keys() )
    keys_l   = list( ret_l["pts"].keys() )
    pts1     = { "uLine_{0}".format( key ):( ret_u["pts"] )[key] for ik,key in enumerate( keys_u ) }
    pts2     = { "lLine_{0}".format( key ):( ret_l["pts"] )[key] for ik,key in enumerate( keys_l ) }
    pts      = pts1 | pts2
    lines    = { "uLine":ul, "lLine":ll, "edge1":edge1, "edge2":edge2 }
    surfs    = { "surf":surf }
    volus    = {}
    ret      = { "pts":pts, "lines":lines, "surfs":surfs, "volus":volus }
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

    s    = np.linspace( 0.0, 1.0, 21 )
    x    = np.copy( s )
    y    = x**2
    z    = np.zeros( (s.shape[0],) )
    Data = np.concatenate( [ x[:,None], y[:,None], z[:,None] ], axis=1 )
    
    make__regionAlongLine( Data=Data )
    

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.01 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.01 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    

