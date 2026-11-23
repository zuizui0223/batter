"""Research-only 3D physical-airspace point-process and observation operators.

*Air is a volume, not stacked 2D surfaces.*  The target is voxel biological
event intensity per cubic metre per time, with source-specific detection and
observation footprints. This does NOT identify 3D bat niche use unless original
field detector q, geometric support and event independence are calibrated.

V0.1 is intentionally small-memory NumPy; no full LAS/LAZ ingestion, no
occlusion reconstruction, no real wildlife source inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import exp, fsum, isfinite, lgamma, log
from typing import Sequence
import numpy as np

SYNTHETIC_BETA_GRID = tuple(-2 + .5 * k for k in range(9))


@dataclass(frozen=True)
class AirVolume:
    centers_m: np.ndarray
    voxel_volume_m3: np.ndarray
    classification: np.ndarray
    horizontal_cell: tuple[str, ...]
    crs: str
    vertical_datum: str = "AGL_m"

    def __post_init__(self):
        pts = np.asarray(self.centers_m, dtype=float)
        v = np.asarray(self.voxel_volume_m3, dtype=float)
        cls = np.asarray(self.classification, dtype=int)
        n = len(pts)
        if pts.shape != (n, 3) or n < 2 or not np.all(np.isfinite(pts)):
            raise ValueError("voxel centres must be finite local projected xyz metres")
        if v.shape != (n,) or not np.all(np.isfinite(v)) or np.any(v <= 0):
            raise ValueError("voxel volumes must be positive finite m3")
        if cls.shape != (n,) or not np.isin(cls, [-1, 0, 1]).all():
            raise ValueError("classification must be -1 unknown, 0 vegetation, 1 known air")
        if not np.any(cls == 1):
            raise ValueError("no source-verified air cells")
        if len(self.horizontal_cell) != n or any(not x for x in self.horizontal_cell):
            raise ValueError("each voxel requires a physical horizontal cell identifier")
        if self.vertical_datum != "AGL_m":
            raise ValueError("height must be measured terrain-relative (AGL_m)")
        # Do not silently use lat/lon degree distance in a physical voxel model.
        if not self.crs or self.crs.lower() in ("epsg:4326", "wgs84", "longitude-latitude"):
            raise ValueError("horizontal positions must use a local projected metric CRS")
        if np.any(pts[:,2] < 0):
            raise ValueError("air voxel height above ground cannot be negative")
        object.__setattr__(self, "centers_m", pts)
        object.__setattr__(self, "voxel_volume_m3", v)
        object.__setattr__(self, "classification", cls)

    @property
    def air(self):
        return self.classification == 1

    @property
    def all_voxels(self):
        return len(self.centers_m)


def regular_air_volume(bounds_m: tuple[float, float, float, float, float, float],
                       edge_m: float,
                       classification: Sequence[int],
                       *,
                       crs: str = "local_projected_m") -> AirVolume:
    """Build a regular 3D grid, with EXPLICIT external air/vegetation/unknown status.

    The returned point coordinates are voxel centres (metres). An absence of
    LiDAR returns does not automatically make a voxel an air voxel.
    """
    x0,x1,y0,y1,z0,z1=tuple(float(x) for x in bounds_m)
    if not isfinite(edge_m) or edge_m <= 0:
        raise ValueError("edge length must be >0")
    spans=[(b-a)/edge_m for a,b in ((x0,x1),(y0,y1),(z0,z1))]
    if any(not isfinite(v) or v < 1 or abs(v-round(v))>1e-10 for v in spans):
        raise ValueError("each bound must contain positive full cubic voxels")
    nx,ny,nz=map(lambda x:int(round(x)),spans)
    if nx*ny*nz>2_000_000:
        raise ValueError("prototype volume too large: use streaming LAZ and tiled masks")
    xs=x0+edge_m*(np.arange(nx)+.5)
    ys=y0+edge_m*(np.arange(ny)+.5)
    zs=z0+edge_m*(np.arange(nz)+.5)
    centers=np.array(list(product(xs,ys,zs)), dtype=float)
    cls=np.asarray(classification,dtype=int)
    keys=tuple(f"x{i}:y{j}" for i in range(nx) for j in range(ny) for k in range(nz))
    return AirVolume(centers,np.full(nx*ny*nz,edge_m**3),cls,keys,crs)


def nearest_vegetation_distance_m(volume: AirVolume, vegetation_returns_m: np.ndarray,
                                  *, chunk: int = 256) -> np.ndarray:
    """Distance to *recorded* vegetation returns, not physical true leaf surface.

    This prototype uses dense point-return distances, O(n_voxels*n_returns)
    CPU; for real TLS/3DEP use a calibrated LAS classifier, spatial index and
    scanner-ray visibility/occlusion mask first.
    """
    pts=np.asarray(vegetation_returns_m,dtype=float)
    if pts.ndim!=2 or pts.shape[1]!=3 or len(pts)==0 or not np.isfinite(pts).all():
        raise ValueError("empty/unvalidated vegetation returns are not open free air")
    if chunk<1 or len(pts)>100_000:
        raise ValueError("prototype point cloud limit: use tiled spatial index")
    d=np.full(volume.all_voxels,np.nan)
    for start in range(0,volume.all_voxels,chunk):
        end=min(start+chunk,volume.all_voxels)
        block=volume.centers_m[start:end]
        squared=((block[:,None,:]-pts[None,:,:])**2).sum(axis=2)
        d[start:end]=np.sqrt(squared.min(axis=1))
    # Unknown/vegetation cells cannot be presented as biological flying-space.
    d[~volume.air]=np.nan
    return d


def clutter_proximity_proxy(distance_m: np.ndarray, scale_m: float) -> np.ndarray:
    """Uncalibrated return-proximity feature in (0,1]; not vegetation biomass."""
    d=np.asarray(distance_m,dtype=float)
    if not isfinite(scale_m) or scale_m<=0:
        raise ValueError("positive metric clutter scale required")
    if np.any(d[np.isfinite(d)]<0):
        raise ValueError("vegetation distances cannot be negative")
    return np.exp(-d/scale_m)


def planar_column_kernel(volume: AirVolume,
                         detection_q: np.ndarray | None = None) -> tuple[np.ndarray, tuple[str,...]]:
    """Records 2D column presence/expected counts by summing *air* voxel rates.

    Detection q=1 is illustrative only; original GBIF source effort is not 1.
    """
    q=np.ones(volume.all_voxels) if detection_q is None else np.asarray(detection_q,dtype=float)
    if q.shape!=(volume.all_voxels,) or not np.isfinite(q).all() or np.any(q<0) or np.any(q>1):
        raise ValueError("planar source detection probability must be finite [0,1]")
    names=tuple(dict.fromkeys(volume.horizontal_cell))
    k=np.zeros((len(names),volume.all_voxels))
    lookup={name:i for i,name in enumerate(names)}
    for i,cell in enumerate(volume.horizontal_cell):
        if volume.air[i]:
            k[lookup[cell],i]=q[i]
    return k,names


def binned_3d_kernel(volume: AirVolume) -> np.ndarray:
    """Idealized exactly localised 3D event count bins (q=1 known only by design)."""
    return np.diag(volume.air.astype(float))


def acoustic_footprint_kernel(volume: AirVolume,
                              microphone_centres_m: np.ndarray,
                              calibrated_q_voxels: np.ndarray,
                              sigma_m: float) -> np.ndarray:
    """Gaussian *hypothetical* acoustic footprint, NOT measured bat beam physics.

    Users must supply calibrated q for species, height and vegetation in a real
    application; this gaussian is a numerical mockup of a known footprint.
    """
    mic=np.asarray(microphone_centres_m,dtype=float)
    q=np.asarray(calibrated_q_voxels,dtype=float)
    if mic.ndim!=2 or mic.shape[1]!=3 or not np.isfinite(mic).all():
        raise ValueError("microphone XYZ must be local projected metres")
    if q.shape!=(volume.all_voxels,) or not np.isfinite(q).all() or np.any(q<0) or np.any(q>1):
        raise ValueError("calibrated detector q must be [0,1] for each voxel")
    if not isfinite(sigma_m) or sigma_m<=0:
        raise ValueError("positive metric acoustic footprint radius required")
    d2=((mic[:,None,:]-volume.centers_m[None,:,:])**2).sum(axis=2)
    return np.exp(-d2/(2*sigma_m**2))*q[None,:]*volume.air[None,:]


def validate_measurements(volume: AirVolume,
                          kernel: np.ndarray,
                          exposure: np.ndarray,
                          y: np.ndarray | None = None) -> tuple[np.ndarray,np.ndarray,np.ndarray | None]:
    k=np.asarray(kernel,dtype=float)
    e=np.asarray(exposure,dtype=float)
    n=volume.all_voxels
    if k.ndim!=2 or k.shape[1]!=n:
        raise ValueError("K is rows=observation units, columns=source air voxels")
    if not np.isfinite(k).all() or np.any(k<0) or np.any(k>1):
        raise ValueError("K cannot be unknown, negative or >1 detection probability")
    if np.any(k[:,~volume.air]!=0):
        raise ValueError("K must have zero support on unknown and vegetation voxels")
    if e.shape!=(k.shape[0],) or np.any(~np.isfinite(e)) or np.any(e<=0):
        raise ValueError("every observation unit needs positive source exposure")
    z=None
    if y is not None:
        z=np.asarray(y,dtype=float)
        if z.shape!=(k.shape[0],) or np.any(~np.isfinite(z)) or np.any(z<0):
            raise ValueError("source counts cannot be missing, negative or nonfinite")
        if np.any(np.abs(z-np.round(z))>1e-9):
            raise ValueError("original event counts must be integer")
    return k,e,z


def expected_counts(volume: AirVolume,
                    intensity_per_m3_per_hour: np.ndarray,
                    kernel: np.ndarray,
                    exposure_hours: np.ndarray) -> np.ndarray:
    k,e,_=validate_measurements(volume,kernel,exposure_hours)
    lam=np.asarray(intensity_per_m3_per_hour,dtype=float)
    if lam.shape!=(volume.all_voxels,) or not np.isfinite(lam).all() or np.any(lam<0):
        raise ValueError("latent voxel intensity must be positive/zero finite")
    if np.any(lam[~volume.air]!=0):
        raise ValueError("no model intensity may occupy unresolved or vegetation volume")
    return e*(k@(lam*volume.voxel_volume_m3))


def poisson_loglik(y: np.ndarray, mu: np.ndarray) -> float:
    yy=np.asarray(y,dtype=float)
    mm=np.asarray(mu,dtype=float)
    if yy.shape!=mm.shape or np.any(~np.isfinite(yy)) or np.any(yy<0) or np.any(np.abs(yy-np.round(yy))>1e-9):
        raise ValueError("source counts not valid independent Poisson integers")
    if np.any(~np.isfinite(mm)) or np.any(mm<0):
        raise ValueError("expected source Poisson count must be >=0")
    if np.any((yy>0)&(mm==0)):
        return float("-inf")
    nz=yy>0
    return float(np.dot(yy[nz],np.log(mm[nz]))-np.sum(mm))


def kernel_rank_diagnostic(volume: AirVolume,kernel: np.ndarray) -> dict:
    k=np.asarray(kernel,dtype=float)
    validate_measurements(volume,k,np.ones(len(k)))
    active=k[:,volume.air]*volume.voxel_volume_m3[volume.air][None,:]
    rank=int(np.linalg.matrix_rank(active))
    ncols=int(volume.air.sum())
    return {"free_air_voxels":ncols,
            "independent_linear_measurement_rank":rank,
            "unidentified_arbitrary_voxel_directions":ncols-rank,
            "arbitrary_voxel_intensities_fully_linearly_identifiable":rank==ncols,
            "does_not_identify_unknown_species_height_specific_detection":True}


def log_intensity(volume: AirVolume,height_feature: np.ndarray,
                  clutter_feature: np.ndarray,
                  intercept: float,beta_height:float,beta_clutter:float) -> np.ndarray:
    h=np.asarray(height_feature,dtype=float)
    c=np.asarray(clutter_feature,dtype=float)
    if h.shape!=(volume.all_voxels,) or c.shape!=h.shape:
        raise ValueError("geometry feature shape must match volume voxels")
    if (not np.all(np.isfinite(h[volume.air])) or not np.all(np.isfinite(c[volume.air]))
            or not all(map(isfinite,(intercept,beta_height,beta_clutter)))):
        raise ValueError("unknown/invalid source air features and model slopes")
    loglam=np.zeros(volume.all_voxels)
    loglam[volume.air]=intercept+beta_height*h[volume.air]+beta_clutter*c[volume.air]
    lam=np.zeros(volume.all_voxels)
    lam[volume.air]=np.exp(loglam[volume.air])
    if not np.isfinite(lam).all():
        raise ValueError("overflowed source latent intensity")
    return lam


def fit_fixed_grid_known_kernel(volume: AirVolume,
                                height:np.ndarray,clutter:np.ndarray,
                                kernel:np.ndarray,exposure:np.ndarray,y:np.ndarray,
                                *,use_clutter:bool) -> tuple[float,float,float]:
    """Minimal calibrated-K Poisson-grid fit; intercept profiled analytically.

    Demonstration only. Cannot fit unknown physical q from the counts and
    should not be used as a real uncalibrated bat niche GLM.
    """
    k,e,yy=validate_measurements(volume,kernel,exposure,y)
    if yy is None or yy.sum()<=0:
        raise ValueError("source count support absent")
    best=None
    params=None
    for bh in SYNTHETIC_BETA_GRID:
        for bc in SYNTHETIC_BETA_GRID if use_clutter else (0.,):
            shape=log_intensity(volume,height,clutter,0.,bh,bc)
            unit=e*(k@(shape*volume.voxel_volume_m3))
            if np.any((yy>0)&(unit<=0)) or unit.sum()<=0:
                continue
            b0=log(float(yy.sum()/unit.sum()))
            fitted=unit*exp(b0)
            objective=poisson_loglik(yy,fitted)
            key=(round(objective,10),-abs(bc),-abs(bh),-bc,-bh)
            if best is None or key>best:
                best=key;params=(b0,bh,bc)
    if params is None:
        raise ValueError("no source-known q model can explain observations")
    return params


def score_known_kernel(volume:AirVolume, height:np.ndarray, clutter:np.ndarray,
                       kernel:np.ndarray,exposure:np.ndarray,y:np.ndarray,
                       coefficients:tuple[float,float,float]) -> float:
    if len(coefficients)!=3:
        raise ValueError("expected a 3-component fitted source intensity")
    lam=log_intensity(volume,height,clutter,*coefficients)
    expected=expected_counts(volume,lam,kernel,exposure)
    return poisson_loglik(y,expected)


def synthetic_multispecies_projection_witness() -> dict:
    """Known two-world same XY observation / different true species-height I.

    Two species, one physical XY cell, two 1-m3 verified air voxels; y=100 for
    both species in both worlds. True species×height MI is not identified by K.
    """
    volume=AirVolume(
        centers_m=np.array([[0.5,0.5,.5],[.5,.5,1.5]]),
        voxel_volume_m3=np.array([1.,1.]),
        classification=np.array([1,1]),
        horizontal_cell=("site0","site0"),
        crs="local_projected_m",
    )
    planar,names=planar_column_kernel(volume)
    a=np.array([[90.,10.],[10.,90.]])
    b=np.array([[50.,50.],[50.,50.]])
    mu_a=[expected_counts(volume,each,planar,np.array([1.]))[0] for each in a]
    mu_b=[expected_counts(volume,each,planar,np.array([1.]))[0] for each in b]
    def info(world):
        p=world/world.sum()
        ps=p.sum(axis=1)
        pz=p.sum(axis=0)
        return float(sum(p[i,j]*log(p[i,j]/(ps[i]*pz[j]))
                         for i in range(2) for j in range(2) if p[i,j]>0))
    return {
        "planar_counts_world_A":mu_a,"planar_counts_world_B":mu_b,
        "latent_species_by_height_info_A_nats":info(a),
        "latent_species_by_height_info_B_nats":info(b),
        "same_observed_planar_data":bool(np.allclose(mu_a,mu_b)),
        "known_planar_kernel_rank":kernel_rank_diagnostic(volume,planar),
        "true_latent_species_height_partition_not_identified":True,
    }
