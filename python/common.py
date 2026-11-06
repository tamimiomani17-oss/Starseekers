"""Shared helpers (paths, params, rasterio env). Not a stage; imported by the numbered scripts."""
import json
import os
import pathlib
import shutil
import tempfile

import rasterio

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
WEB = ROOT / "web" / "data"
CONFIG = ROOT / "config"

DTM_URL = ("https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/"
           "JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif")
DTM_LOCAL = RAW / "JEZ_hirise_soc_006_1m.tif"
TI_URL = "https://zenodo.org/record/4931348/files/Jezero_Thermal_Inertia_v1.tiff"
TI_LOCAL = RAW / "Jezero_Thermal_Inertia_v1.tiff"


def params():
    return json.loads((CONFIG / "params.json").read_text(encoding="utf-8"))


def rio_env():
    """rasterio.Env that also works when the project path has non-ASCII chars (curl CA file issue on Windows)."""
    import certifi
    ca = pathlib.Path(tempfile.gettempdir()) / "starseekers_cacert.pem"
    if not ca.exists():
        shutil.copyfile(certifi.where(), ca)
    cav = str(ca).replace("\\", "/")
    return rasterio.Env(CURL_CA_BUNDLE=cav, GDAL_CURL_CA_BUNDLE=cav, GDAL_HTTP_USERAGENT="starseekers-prototype",
                        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR")


def dtm_path():
    """Local DTM if downloaded, otherwise the remote one (range reads)."""
    return str(DTM_LOCAL) if DTM_LOCAL.exists() else "/vsicurl/" + DTM_URL
