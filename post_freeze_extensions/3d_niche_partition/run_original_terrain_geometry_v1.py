#!/usr/bin/env python3
# Compatibility copy of the frozen SRTM tile/interpolation helpers.
# Function bodies below are copied from post-freeze/3d-niche-partition-v1.
import gzip
import hashlib
import math
import numpy as np
import requests

UA={"User-Agent":"batter-original-terrain-geometry-v1/1.0"}

def parse_tile_sw(tile):
    lat=int(tile[1:3])*(1 if tile[0]=="N" else -1)
    lon=int(tile[4:7])*(1 if tile[3]=="E" else -1)
    return lat,lon


def tile_id(lat,lon):
    lat_sw=math.floor(float(lat)); lon_sw=math.floor(float(lon))
    return ("N" if lat_sw>=0 else "S")+f"{abs(lat_sw):02d}"+("E" if lon_sw>=0 else "W")+f"{abs(lon_sw):03d}"


def load_tiles(panel_receipt,void_value):
    grids={}
    for info in panel_receipt["tiles"]:
        rr=requests.get(info["url"],headers=UA,timeout=300)
        rr.raise_for_status()
        blob=rr.content
        if hashlib.sha256(blob).hexdigest()!=info["gzip_sha256"]:
            raise RuntimeError(f"{info['tile']}: gzip SHA mismatch")
        raw=gzip.decompress(blob)
        n=int(info["grid_n"])
        if len(raw)!=n*n*2:
            raise RuntimeError(f"{info['tile']}: uncompressed bytes {len(raw)} != {n*n*2}")
        arr=np.frombuffer(raw,dtype=">i2").reshape((n,n))
        grids[info["tile"]]=arr
    return grids


def bilinear_hgt(grids,lat,lon,void_value):
    tile=tile_id(lat,lon)
    if tile not in grids:
        raise RuntimeError(f"missing pinned tile {tile}")
    arr=grids[tile];n=arr.shape[0]
    lat0,lon0=parse_tile_sw(tile)
    row=(lat0+1.0-float(lat))*(n-1)
    col=(float(lon)-lon0)*(n-1)
    if not (0<=row<=n-1 and 0<=col<=n-1):
        raise RuntimeError(f"{tile}: point outside tile")
    r0=int(math.floor(row));c0=int(math.floor(col))
    r1=min(r0+1,n-1);c1=min(c0+1,n-1)
    vals=np.array([arr[r0,c0],arr[r0,c1],arr[r1,c0],arr[r1,c1]],dtype=float)
    if np.any(vals==void_value):
        raise RuntimeError(f"{tile}: DEM void touched")
    dr=row-r0;dc=col-c0
    v00,v01,v10,v11=vals
    return float(v00*(1-dr)*(1-dc)+v01*(1-dr)*dc+v10*dr*(1-dc)+v11*dr*dc)


