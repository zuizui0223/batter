"""Source-aware source-local thermal XYZ to surveyed world XYZ registration.

*Not* a georeferencing algorithm that can recover undocumented locations.
Requires at least 3 independent noncollinear tied fiducials, 1 separate
validation fiducial, explicit source distance calibration and surveyed
projected horizontal/vertical datums. No real Münster controls are supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import re
import numpy as np

SOURCE_SCALE_MIN_SINGULAR_RATIO=0.01
DEFAULT_MAX_RMS_FIT_M=0.5
DEFAULT_MAX_HELDOUT_ERROR_M=0.5


@dataclass(frozen=True)
class SurveyedRegistration:
    rotation:np.ndarray
    translation_m:np.ndarray
    source_m_per_unit:float
    world_horizontal_epsg:str
    world_vertical_datum:str
    calibration_rms_m:float
    heldout_max_error_m:float
    n_calibration_fiducials:int
    n_independent_validation_fiducials:int

    def apply(self,local_xyz:np.ndarray)->np.ndarray:
        raw=np.asarray(local_xyz,dtype=float)
        if raw.ndim!=2 or raw.shape[1]!=3 or not np.isfinite(raw).all():
            raise ValueError("new local XYZ points must be all finite 3-vectors")
        return raw*self.source_m_per_unit@self.rotation.T + self.translation_m

    def to_agl(self,world_xyz:np.ndarray,ground_DTM_elevation_m:np.ndarray,
               *,ground_vertical_datum:str)->np.ndarray:
        """Only convert world z to AGL with an independently matching DTM.

        Does not verify the DTM acquisition, semantic ground classes, XY
        georeferencing or source visibility; caller must independently audit.
        """
        xyz=np.asarray(world_xyz,dtype=float)
        dtm=np.asarray(ground_DTM_elevation_m,dtype=float)
        if ground_vertical_datum != self.world_vertical_datum:
            raise ValueError("DTM vertical datum must equal surveyed world vertical datum")
        if (xyz.ndim!=2 or xyz.shape[1]!=3 or dtm.shape!=(len(xyz),)
                or not np.isfinite(xyz).all() or not np.isfinite(dtm).all()):
            raise ValueError("source DTM ground heights and world positions must be finite")
        agl=xyz[:,2]-dtm
        if np.any(agl<0):
            raise ValueError("position below surveyed ground, cannot treat as in air")
        return agl


def _as_control_points(values:np.ndarray,name:str,min_n:int)->np.ndarray:
    pts=np.asarray(values,dtype=float)
    if pts.ndim!=2 or pts.shape[1]!=3 or len(pts)<min_n or not np.isfinite(pts).all():
        raise ValueError(name+" requires finite Nx3 metric control points")
    return pts


def _spatial_baseline_valid(points:np.ndarray,name:str):
    singular=np.linalg.svd(points-points.mean(axis=0),compute_uv=False)
    if singular[0]<1e-10 or singular[1]/singular[0]<SOURCE_SCALE_MIN_SINGULAR_RATIO:
        raise ValueError(name+" surveyed tie-point layout is coincident/collinear/ill-conditioned")


def _world_crs_valid(label:str)->bool:
    # EPSG:25832 ETRS89 / UTM32N or EPSG:32632 WGS84 / UTM32N
    # are projected in metres. Geographic 4xxx EPSGs are deliberately
    # refused. This is only a guard, not a CRS transformation library.
    m=re.fullmatch(r"EPSG:(\d{4,6})",label.strip(),re.IGNORECASE) if isinstance(label,str) else None
    if not m:
        return False
    code=int(m.group(1))
    return code not in (4326,4258,4269,4978,4979) and code>=2000


def fit_surveyed_rigid_registration(
        local_calibration_xyz:np.ndarray,
        surveyed_world_calibration_xyz_m:np.ndarray,
        local_validation_xyz:np.ndarray,
        surveyed_world_validation_xyz_m:np.ndarray,
        *,
        source_m_per_unit:float|None,
        world_horizontal_epsg:str,
        world_vertical_datum:str,
        max_calibration_rms_m:float=DEFAULT_MAX_RMS_FIT_M,
        max_independent_validation_error_m:float=DEFAULT_MAX_HELDOUT_ERROR_M,
    ) -> SurveyedRegistration:
    """Known-scale 3D Kabsch transform from independent control correspondences.

    The fit is validated on controls withheld from its SVD computation. It
    must not be applied to an actual bat source with only a single lamppost
    (or missing true world control coordinates), even if synthetic tests pass.
    """
    if source_m_per_unit is None or not isfinite(source_m_per_unit) or source_m_per_unit<=0:
        raise ValueError("source local XYZ metre-per-unit scale must be independently verified")
    if not _world_crs_valid(world_horizontal_epsg):
        raise ValueError("world CRS must be a documented projected metric EPSG, not lat/lon")
    if (not isinstance(world_vertical_datum,str) or len(world_vertical_datum.strip())<3
            or world_vertical_datum.strip().lower() in (
                "unknown","none","local","agl","msl","vertical_unknown")):
        raise ValueError("world source surveyed vertical datum must be specific and independently known")
    if (not all(isfinite(x) and x>0 for x in
                (max_calibration_rms_m,max_independent_validation_error_m))):
        raise ValueError("explicit metre QC tolerances required")
    x=_as_control_points(local_calibration_xyz,"source calibration",3)*source_m_per_unit
    y=_as_control_points(surveyed_world_calibration_xyz_m,"world calibration",3)
    vx=_as_control_points(local_validation_xyz,"independent local validation",1)*source_m_per_unit
    vy=_as_control_points(surveyed_world_validation_xyz_m,"independent world validation",1)
    if len(x)!=len(y) or len(vx)!=len(vy):
        raise ValueError("tie-point correspondence counts must match")
    _spatial_baseline_valid(x,"source")
    _spatial_baseline_valid(y,"world")
    xcenter=x.mean(axis=0)
    ycenter=y.mean(axis=0)
    U,_,Vh=np.linalg.svd((x-xcenter).T@(y-ycenter))
    reflection=np.diag([1.,1.,np.sign(np.linalg.det(Vh.T@U.T))])
    R=Vh.T@reflection@U.T
    if np.linalg.det(R)<1-1e-10:
        raise ValueError("proper 3D rotation determinant must be positive one")
    translation=ycenter-xcenter@R.T
    fitted=x@R.T+translation
    fit_error=np.linalg.norm(fitted-y,axis=1)
    independent_error=np.linalg.norm(vx@R.T+translation-vy,axis=1)
    rms=float(np.sqrt(np.mean(fit_error**2)))
    maximum=float(independent_error.max())
    if rms>max_calibration_rms_m or maximum>max_independent_validation_error_m:
        raise ValueError("independently surveyed rigid registration residual exceeds predeclared threshold")
    return SurveyedRegistration(
        rotation=R,
        translation_m=translation,
        source_m_per_unit=float(source_m_per_unit),
        world_horizontal_epsg=world_horizontal_epsg,
        world_vertical_datum=world_vertical_datum,
        calibration_rms_m=rms,
        heldout_max_error_m=maximum,
        n_calibration_fiducials=len(x),
        n_independent_validation_fiducials=len(vx),
    )
