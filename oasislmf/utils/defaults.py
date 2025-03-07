__all__ = [
    'get_config_profile',
    'get_default_accounts_profile',
    'get_default_deterministic_analysis_settings',
    'get_default_exposure_profile',
    'get_default_fm_profile_field_values',
    'get_default_step_policies_profile',
    'get_default_fm_aggregation_profile',
    'get_default_unified_profile',
    'assign_defaults_to_il_inputs',
    'store_exposure_fp',
    'find_exposure_fp',
    'DAMAGE_GROUP_ID_COLS',
    'HAZARD_GROUP_ID_COLS',
    'CORRELATION_GROUP_ID',
    'API_EXAMPLE_AUTH',
    'DEFAULT_RTREE_INDEX_PROPS',
    'KTOOLS_ALLOC_GUL_MAX',
    'KTOOLS_ALLOC_FM_MAX',
    'KTOOLS_FIFO_RELATIVE',
    'KTOOLS_DEBUG',
    'KTOOLS_DISABLE_ERR_GUARD',
    'KTOOLS_NUM_PROCESSES',
    'KTOOLS_GUL_LEGACY_STREAM',
    'OASIS_FILES_PREFIXES',
    'SUMMARY_MAPPING',
    'SUMMARY_OUTPUT',
    'SOURCE_IDX',
    'STATIC_DATA_FP',
    'WRITE_CHUNKSIZE',
    'KTOOLS_ALLOC_IL_DEFAULT',
    'KTOOLS_ALLOC_RI_DEFAULT',
]

import glob
import io
import json
import os
from collections import OrderedDict

from .exceptions import OasisException
from .fm import SUPPORTED_FM_LEVELS

try:
    from json import JSONDecodeError
except ImportError:
    from builtins import ValueError as JSONDecodeError

SOURCE_FILENAMES = OrderedDict({
    'loc': 'location.csv',
    'acc': 'account.csv',
    'info': 'ri_info.csv',
    'scope': 'ri_scope.csv',
    'complex_lookup': 'analysis_settings.json',
    'oed_location_csv': 'location.csv',
    'oed_accounts_csv': 'account.csv',
    'oed_info_csv': 'ri_info.csv',
    'oed_scope_csv': 'ri_scope.csv',
    'lookup_config_json': 'lookup.json',
    'profile_loc_json': 'profile_location.json',
    'keys_data_csv': 'keys.csv',
    'model_version_csv': 'model_version.csv',
    'lookup_complex_config_json': 'lookup_complex.json',
    'profile_acc_json': 'profile_account.json',
    'profile_fm_agg_json': 'profile_fm_agg.json',
})

API_EXAMPLE_AUTH = OrderedDict({
    'user': 'admin',
    'pass': 'password',
})

DEFAULT_RTREE_INDEX_PROPS = {
    'buffering_capacity': 10,
    'custom_storage_callbacks': None,
    'custom_storage_callbacks_size': 0,
    'dat_extension': 'dat',
    'dimension': 2,
    'filename': '',
    'fill_factor': 0.7,
    'idx_extension': 'idx',
    'index_capacity': 100,
    'index_id': None,
    'leaf_capacity': 100,
    'near_minimum_overlap_factor': 32,
    'overwrite': True,
    'pagesize': 4096,
    'point_pool_capacity': 500,
    'region_pool_capacity': 1000,
    'reinsert_factor': 0.3,
    'split_distribution_factor': 0.4,
    'storage': 0,
    'tight_mbr': True,
    'tpr_horizon': 20.0,
    'type': 0,
    'variant': 2,
    'writethrough': False
}

MAPPING_FROM_ODS_SPEC = {
    "Type & Description": "desc",
    "Required Field": "require_field",
    "Data Type": "data_type",
    "Allow blanks?": "null_allowed",
    "Default": "default_value",
    "Valid value range": "valid_range",
    "SecMod?": "secmod",
    "BackEndTableName": "db_tablename",
    "Back End DB Field Name": "db_fieldname",
    "pd_dtype": "py_dtype",
    "File Name": "filename"
}

# Store index from merged source files (for later slice & dice)
SOURCE_IDX = OrderedDict({
    'loc': 'loc_idx',
    'acc': 'acc_idx',
    'info': 'info_idx',
    'scope': 'scope_idx'
})

SAR_ID = 'loc_id'  # name of the column that serve as a subject at risk id, historically loc_id

SUMMARY_MAPPING = OrderedDict({
    'gul_map_fn': 'gul_summary_map.csv',
    'fm_map_fn': 'fm_summary_map.csv'
})

SUMMARY_OUTPUT = OrderedDict({
    'gul': 'gulsummaryxref.csv',
    'il': 'fmsummaryxref.csv'
})

SUMMARY_TOP_LEVEL_COLS = ['layer_id', SOURCE_IDX['acc'], 'PolNumber']

# Path for storing static data/metadata files used in the package
STATIC_DATA_FP = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), '_data')


# Default profiles that describe the financial terms in the OED acc. and loc.
# (exposure) files, as well as how aggregation of FM input items is performed
# in the different OED FM levels


def store_exposure_fp(fp, exposure_type):
    """
    Preserve original exposure file extention if its in a pandas supported
    compressed format

    compression : {‘infer’, ‘gzip’, ‘bz2’, ‘zip’, ‘xz’, None}, default ‘infer’
                  For on-the-fly decompression of on-disk data. If ‘infer’ and
                  filepath_or_buffer is path-like, then detect compression from
                  the following extensions: ‘.gz’, ‘.bz2’, ‘.zip’, or ‘.xz’
                  (otherwise no decompression).

                  If using ‘zip’, the ZIP file must contain only one data file
                  to be read in. Set to None for no decompression.

                New in version 0.18.1: support for ‘zip’ and ‘xz’ compression.
    """
    compressed_ext = ('.gz', '.bz2', '.zip', '.xz', '.parquet')
    filename = SOURCE_FILENAMES[exposure_type]
    if fp.endswith(compressed_ext):
        return '.'.join([filename, fp.rsplit('.')[-1]])
    else:
        return filename


def find_exposure_fp(input_dir, exposure_type, required=True):
    """
    Find an OED exposure file stored in the oasis inputs dir
    while preserving the compressed ext
    """
    fp = glob.glob(os.path.join(input_dir, SOURCE_FILENAMES[exposure_type].rsplit(".", 1)[0] + '*'))
    if required or fp:
        return fp.pop()


def get_default_json(src_fp):
    """
    Loads JSON from file.

    :param src_fp: Source JSON file path
    :type src_fp: str

    :return: dict
    :rtype: dict
    """
    try:
        with io.open(src_fp, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, JSONDecodeError, OSError, TypeError):
        raise OasisException('Error trying to load JSON from {}'.format(src_fp))


def get_default_accounts_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_acc_profile.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_default_exposure_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_loc_profile.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_default_fm_profile_field_values(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_fm_profile_field_values.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_default_step_policies_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_step_policies_profile.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_config_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'config_compatibility_profile.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_default_unified_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_unified_profile.json')
    return get_default_json(src_fp=fp) if not path else fp


def get_default_fm_aggregation_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_fm_agg_profile.json')
    return {int(k): v for k, v in get_default_json(src_fp=fp).items()} if not path else fp


def assign_defaults_to_il_inputs(df):
    """
    Assign default values to IL inputs.

    :param df: IL input items dataframe
    :type df: pandas.DataFrame

    :return: IL input items dataframe
    :rtype: pandas.DataFrame
    """
    # Get default values for IL inputs
    default_fm_profile_field_values = get_default_fm_profile_field_values()

    for level in default_fm_profile_field_values.keys():
        level_id = SUPPORTED_FM_LEVELS[level]['id']
        for k, v in default_fm_profile_field_values[level].items():
            # Evaluate condition for assigning default values if present
            if v.get('condition'):
                df.loc[df.level_id == level_id, k] = df.loc[
                    df.level_id == level_id, k
                ].where(eval(
                    'df.loc[df.level_id == level_id, k]' + v['condition']),
                    v['default_value']
                )
            else:
                df.loc[df.level_id == level_id, k] = v['default_value']

    return df


WRITE_CHUNKSIZE = 2 * (10 ** 5)

DAMAGE_GROUP_ID_COLS = ["PortNumber", "AccNumber", "LocNumber"]
HAZARD_GROUP_ID_COLS = ["PortNumber", "AccNumber", "LocNumber"]

CORRELATION_GROUP_ID = ['CorrelationGroup']

# Default name prefixes of the Oasis input files (GUL + IL)
OASIS_FILES_PREFIXES = OrderedDict({
    'gul': {
        'complex_items': 'complex_items',
        'items': 'items',
        'coverages': 'coverages',
        'amplifications': 'amplifications',
        'sections': 'sections',
        'item_adjustments': 'item_adjustments'
    },
    'il': {
        'fm_policytc': 'fm_policytc',
        'fm_profile': 'fm_profile',
        'fm_programme': 'fm_programme',
        'fm_xref': 'fm_xref',
    }
})


# Default analysis settings for deterministic loss generation
def get_default_deterministic_analysis_settings(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'analysis_settings.json')
    return get_default_json(src_fp=fp) if not path else fp


# Defaults for Ktools runtime parameters
KTOOLS_NUM_PROCESSES = -1
KTOOLS_FIFO_RELATIVE = False
KTOOLS_DISABLE_ERR_GUARD = False
KTOOLS_GUL_LEGACY_STREAM = False
# ktools gul alloc rules:
# 3 = total loss using multiplicative method
# 2 = total loss is maximum subperil loss
# 1 = default with back allocation
# 0 = default without back allocation
KTOOLS_ALLOC_GUL_MAX = 3
KTOOLS_ALLOC_FM_MAX = 3
KTOOLS_ALLOC_GUL_DEFAULT = 0
KTOOLS_ALLOC_IL_DEFAULT = 2
KTOOLS_ALLOC_RI_DEFAULT = 3
KTOOLS_TIV_SAMPLE = -2
KTOOLS_MEAN_SAMPLE_IDX = -1
KTOOLS_STD_DEV_SAMPLE_IDX = -2
KTOOLS_TIV_SAMPLE_IDX = -3
KTOOL_N_GUL_PER_LB = 0
KTOOL_N_FM_PER_LB = 0

# Values for event shuffle rules
EVE_NO_SHUFFLE = 0
EVE_ROUND_ROBIN = 1
EVE_FISHER_YATES = 2
EVE_STD_SHUFFLE = 3
EVE_DEFAULT_SHUFFLE = EVE_ROUND_ROBIN

KTOOLS_DEBUG = False
