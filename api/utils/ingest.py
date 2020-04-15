"""
Ingest

Load local and remote data into database.
"""
import pandas as pd
from time import time
from functools import partial

from .loader import load
from .writer import *
from .transform import *
from api.models import *

import logging

ingestlogger = logging.getLogger('.'.join(['api.app', __name__.strip('api.')]))


class Ingest:
    """
    :param category: trial or product source
    :param source: source URI or filepath
    :type category: str; valid=trial, product
    :type source: str or buffer
    """

    def __init__(self, source, category: str = None, **kwargs):
        self.category = category
        self.source = source
        self.start_time = time()
        self.data = load(source, **kwargs)
        self.assign_transformations()
        self.assign_writer()

    def assign_transformations(self):
        if self.category == "trial":
            self._transforms = assign_trial_transforms()
        elif self.category == "product":
            self._transforms = assign_product_transforms()
        elif self.category in ['country', 'milestone']:
            # Factory tables should not need any filtering
            self._transforms = [null_transform]
        else:
            raise ValueError("Invalid Category Type")

    def assign_writer(self):
        try:
            self._writer = eval(f"write_{self.category}")
        except Exception as e:
            ingestlogger.error(f'Could not assign writer for \
                {self.category}. {e}')

    def transform_data(self):
        self._transformed_data = self.data.copy()
        for transform in self._transforms:
            self._transformed_data = transform(self._transformed_data)

    def write_data(self):
        if self._transformed_data is not None:
            self._writer(self._transformed_data)
        else:
            error_msg = "Attempting to write Nonetype.  Transform data first."
            ingestlogger.error(error_msg)
            raise ValueError(error_msg)


### Control Function ###


def run_ingest(source, category: str, **kwargs):
    ingestlogger.info(f"Starting ingest of source: {source} category: {category}")

    try:  # will start load automatically
        job = Ingest(source=source, category=category, **kwargs)
        process_time = time() - job.start_time
        ingestlogger.info(f"Load completed in: {process_time}")
    except Exception as e:
        ingestlogger.error(f"Load failed. \n {e}")
        return "error"  # return statement for unittest
    # Transform Data & Log
    try:
        job.transform_data()
        ingestlogger.info(
            f"Transformation completed in: {(time() - job.start_time) - process_time}"
        )
        process_time = time() - job.start_time
    except Exception as e:
        ingestlogger.error(f"Transformation failed. \n {e}")
        return "error"  # return statement for unittest
    # Write Data & Log
    try:
        job.write_data()
        ingestlogger.info(
            f"Data write completed in: {(time() - job.start_time) - process_time}"
        )
        process_time = time() - job.start_time
    except Exception as e:
        ingestlogger.error(f"Write failed. \n {e}")
        return "error"  # return statement for unittest

    ingestlogger.info(f"Ingest completed in {time() - job.start_time}")


#########################
### Common Transforms ###
#########################


def null_transform(data: pd.DataFrame):
    return data


def make_column_filter(model):
    return partial(filter_columns, model=model)


##################
### Trial Data ###
##################


def assign_trial_transforms(**kwargs):
    """Assemble trial data transforms for clean write"""
    transform_list = [
        null_transform,
        trial_cleaner,
        infer_trial_products,
        make_column_filter(TrialRaw),
        cast_dates,
        clean_null,
        # Add transforms here or
        # use transform_list.append(new_transform) for dynamic construction
    ]
    return transform_list


####################
### Product Data ###
####################


def assign_product_transforms(**kwargs):
    """Assemble trial data transforms for clean write"""
    transform_list = [
        null_transform,
        clean_product_raw,
        make_column_filter(ProductRaw),
        cast_dates,
        clean_null,
        # Add transforms here or
        # use transform_list.append(new_transform) for dynamic construction
    ]
    return transform_list
