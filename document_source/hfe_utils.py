# utility module for working with Apollo HFE data from various sources

from collections import defaultdict
import datetime as dt
from itertools import product
import os
import re

import astropy.time as atime
import numpy as np
import pandas as pd


class NestingDict(defaultdict):
    """
    shorthand for automatically-nesting dictionary -- i.e.,
    insert a series of keys at any depth into a NestingDict
    and it automatically creates all needed levels above.
    """
    def __init__(self):
        super().__init__()
        self.default_factory = NestingDict

    __repr__ = dict.__repr__


def base_hfe_filenames():
    """
    return an iterator over the cartesian product of
    mission / probe / sensor (bridge).
    shorthand way to do nested-for-loops over the canonical HFE
    'files.'
    """
    return product(["a15", "a17"], ["p1", "p2"], [1, 2, 3, 4, 5])


def tree_tuples(dictionary):
    """
    make list of tuples of 'paths' of keys by
    depth-first traversing nested dictionaries or similar.
    shorthand way to nested-for-loop through nested
    mapping-like structures.
    """
    paths = []

    def keydive(level, shared_path_list, parent_keys=None):
        if parent_keys is None:
            parent_keys = []
        try:
            keys = dict.keys(level)
            # many classes have a keys() method
            # so with level.keys() / AttributeError
            # we, like, dive whole arrays
            # which is a different thing
        except TypeError:
            shared_path_list.append(tuple(parent_keys))
            return
        return [
            keydive(level[key], shared_path_list, parent_keys + [key])
            for key in keys
        ]

    keydive(dictionary, paths)
    return paths


def load_hfe(pathname="."):
    """
    loads uncorrected 2005 NSSDC data into a nested diectionary of
    pandas DataFrames.
    """
    data = NestingDict()
    # uncorrected 2005 NSSDC data
    # cartesian product of probe parameters
    for mission, probe, sensor in base_hfe_filenames():
        filename = "{pathname}/{m}/{m}_hfe_{p}_{s}.tab".format(
            pathname=pathname, m=mission, p=probe, s=sensor
        )
        columns = (
            ["Time", "HTR", "TREF", "TC1", "TC2", "TC3", "TC4"]
            if sensor == 3
            else ["Time", "dT", "T"]
        )
        data[mission][probe][sensor] = pd.read_csv(
            filename,
            skiprows=2,
            names=columns,
            delim_whitespace=True,
            skipinitialspace=True,
        )
    return data


def flag_missing_hfe(data):
    """
    Flag rows with any missing data values of -9999. Nagihara data don't use
    this convention (they simply don't include any missing points), but we
    create the flags column while we're at it.
    we do *not* exclude values where HTR data is missing; HTR data
    is essentially unusable, but thermocouple/reference bridge data isn't.
    """
    for mission, probe, sensor in tree_tuples(data):
        data[mission][probe][sensor]["flags"] = 0

        if sensor == 3:
            # thermocouple / reference bridge files
            data[mission][probe][sensor].loc[
                (data[mission][probe][sensor]["Time"] == -9999)
                | (data[mission][probe][sensor]["TC1"] == -9999)
                | (data[mission][probe][sensor]["TC2"] == -9999)
                | (data[mission][probe][sensor]["TC3"] == -9999)
                | (data[mission][probe][sensor]["TC4"] == -9999),
                "flags",
            ] += 0b1
        else:
            # differential thermometer files
            data[mission][probe][sensor].loc[
                (data[mission][probe][sensor]["dT"] == -9999)
                | (data[mission][probe][sensor]["T"] == -9999)
                | (data[mission][probe][sensor]["Time"] == -9999),
                "flags",
            ] += 0b1


def manage_disordered_hfe(data):
    """
    flags time-inverted pairs of points in NSSDC data. then sorts all sets
    by time, which also fixes some misplaced time ranges in the Nagihara
    paper data. checks all sets, although this is a bit wasteful.
    """
    for mission, probe, sensor in tree_tuples(data):
        if mission in ["a15", "a17"]:
            flags = np.array(data[mission][probe][sensor]["flags"])
            for i in np.arange(data[mission][probe][sensor]["Time"].size - 1):
                if (
                        data[mission][probe][sensor]["Time"][i + 1]
                        - data[mission][probe][sensor]["Time"][i]
                        <= 0
                        and data[mission][probe][sensor]["Time"][i] != -9999
                        and data[mission][probe][sensor]["Time"][
                    i + 1] != -9999
                ):
                    flags[i] += 0b10000000000
                    flags[i + 1] += 0b10000000000
            data[mission][probe][sensor]["flags"] = flags
        data[mission][probe][sensor] = data[mission][probe][sensor] \
            .sort_values(by="Time").reset_index(drop=True)


# functions for writing out reduced sets.

def add_crlf_ending(filename):
    """Converts final terminator of file to CRLF for PDS4 compatibility"""
    if os.linesep != "\r\n":
        with open(filename, "rb") as file:
            needs_terminator = file.read()
        has_terminator = needs_terminator[:-1] + b"\r\n"
        with open(filename, "wb") as file:
            file.write(has_terminator)


def write_clean_hfe(data, outpath=".", version=""):
    """
    standardize number and column formats,
    then write 'clean' set out to disk
    """
    # make output directories
    if not os.path.exists(outpath):
        os.mkdir(outpath)
        os.mkdir(outpath + "/a15")
        os.mkdir(outpath + "/a17")

    # put columns in label-specified order
    for mission, probe, sensor in tree_tuples(data):
        frame = data[mission][probe][sensor].copy()
        if "dT_corr" in frame.columns:
            frame = frame.reindex(
                columns=["Time", "T", "dT", "dT_corr", "flags"],
            )
        elif sensor == 3:
            frame = frame.reindex(
                columns=[
                    "Time",
                    "HTR",
                    "TREF",
                    "TC1",
                    "TC2",
                    "TC3",
                    "TC4",
                    "flags",
                ],
            )
        else:
            frame = frame.reindex(
                columns=["Time", "T", "dT", "flags"],
            )

        # enforce IBM 1130-equivalent number representation

        for column in frame.columns:
            # with one twist: allow millisecond precision in the Nagihara data
            if (mission[3:4] == "_") and (column == "Time"):
                frame[column] = frame[column].apply(
                    "{:.11E}".format
                ).str.pad(17, "right")
            else:
                frame[column] = frame[column].apply(
                    "{:.7E}".format
                ).str.pad(14, "right")

        # the following series of ugly regex substitutions is required because
        # of deficiencies in fixed-width table formatting in pandas,
        # exacerbated by a regression in pandas.to_string 0.25 that inserts
        # leading spaces in non-indexed output.

        table = re.sub(
            r"\n\s(\d|-)",
            r"\n\1",
            frame.to_string(
                index=False, justify="left"
            ),
        )
        table = re.sub(r" (?= (\d|-))", r"", table)
        # create correct line endings when script run from any major OS
        table = re.sub(r"(\n)|(\r\n)|(\r)", r"\r\n", table)

        filename = "{outpath}/{m}{p}f{s}{v}.tab".format(
            outpath=outpath + "/" + mission[0:3],
            m=mission,
            p=probe,
            s=sensor,
            v=version,
        )
        with open(filename, "w", ) as output_file:
            print(table, file=output_file)
        # and then put a crlf on at the end for good measure
        add_crlf_ending(filename)


def write_split_hfe(data, outpath=".", version=""):
    """formatting / writing function for 'split' dataset"""
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    for mission, probe, sensor in base_hfe_filenames():
        output = data[mission][probe][sensor].copy()
        output["Time"] = output["Time"] \
                             .dt.strftime("%Y-%m-%dT%H:%M:%S.%f") \
                             .str.slice(0, -3) + "Z"
        filename = "{outpath}/{m}{p}f{s}{v}_split.tab".format(
            outpath=outpath, m=mission, p=probe, s=sensor, v=version
        )
        output.to_csv(filename, index=False, line_terminator="\r\n")


def write_deep_hfe(data, outpath=".", version=""):
    """formatting / writing function for 'depth"""
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    for mission, probe in tree_tuples(data):
        data_deep_out = data[mission][probe].copy()
        data_deep_out["Time"] = (
                data_deep_out["Time"]
                .dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
                .str.slice(0, -3)
                + "Z"
        )
        filename = "{outpath}/{m}{p}{v}_depth.tab".format(
            outpath=outpath, m=mission, p=probe, v=version
        )
        data_deep_out.to_csv(
            filename, index=False, line_terminator="\r\n",
        )


# Functions for interpreting data released by Nagihara et. al along with their
# 2018 paper "Examination of the Long-Term Subsurface Warming Observed at the
# Apollo 15 and 17 Sites Utilizing the Newly Restored Heat Flow Experiment Data
# From 1975 to 1977." Output intended primarily as intermediate data for
# further correction and reduction by other utilities in this module.

# The original reduced Apollo HFE data uses an epoch time format: milliseconds
# from 24 hours before the beginning of the mission's start year. This is
# December 31, 1970 for Apollo 15, and December 31, 1971 for Apollo 17. These
# functions convert between Gregorian time and mission epoch time.

# epoch-to-Gregorian functions. placing in TAI to avoid leap second weirdness.
# excessive digits of precision are for parity with internal astropy values.


def a15_to_greg(time):
    epoch = dt.datetime(1970, 12, 31, 0, 0, 8, 943570)
    return epoch + dt.timedelta(milliseconds=time)


def a17_to_greg(time):
    epoch = dt.datetime(1971, 12, 31, 0, 0, 9, 889650)
    return epoch + dt.timedelta(milliseconds=time)


# Gregorian-to-epoch functions (assume TAI input)

def a15_time(time):
    """Gregorian-to-a15-epoch (assume TAI input)"""
    if time is not None:
        epoch = dt.datetime(1970, 12, 31, 0, 0, 8, 943570)
        return (time - epoch).total_seconds() * 1000
    return None


def a17_time(time):
    """Gregorian-to-a17-epoch (assume TAI input)"""
    if time is not None:
        epoch = dt.datetime(1971, 12, 31, 0, 0, 9, 889650)
        return (time - epoch).total_seconds() * 1000
    return None


def tai_to_utc(time):
    """
    utility function for converting between TAI and UTC. this allows us to use
    astropy to deal with leap seconds without later doing large table
    comparisons between astropy Time objects (much slower than using datetime).
    """
    return atime.Time(time, scale="tai").utc.datetime


def utc_to_tai(time):
    """
    utility function for converting between UTC and TAI. this allows us to use
    astropy to deal with leap seconds without later doing large table
    comparisons between astropy Time objects (much slower than using datetime).
    """

    # 9999 flags empty rows in nagihara 2018 spreadsheet.
    if not time == dt.datetime(9999, 1, 1, 0, 0, 0):
        return atime.Time(time, scale="utc").tai.datetime


# silly utility functions for vectorizing over Nagihara datelists. 9999
# flags empty rows.

def seconds_interval(time):
    """timedelta in seconds from number, converting nans to 0"""
    if not np.isnan(time):
        return dt.timedelta(seconds=time)
    return dt.timedelta(0)


def days_since_year(day, year):
    """return a datetime object from a given year + day offset"""
    if not np.isnan(day):
        return dt.datetime(year, 1, 1) + dt.timedelta(days=(int(day) - 1))
    return dt.datetime(9999, 1, 1, 0, 0, 0)


def nagihara_doy_to_dt(nagihara_time):
    """
    Nagihara PDS release uses DOY format; this simply breaks it up to datetime
    equivalent. might be better to use strptime.
    """
    year = dt.datetime(int(nagihara_time[0:4]), 1, 1, 0, 0)
    day_of_year = dt.timedelta(days=int(nagihara_time[5:8]) - 1)
    hour = dt.timedelta(hours=int(nagihara_time[9:11]))
    minute = dt.timedelta(minutes=int(nagihara_time[12:14]))
    second = dt.timedelta(seconds=float(nagihara_time[15:21]))
    return year + day_of_year + hour + minute + second


# main function for ingesting data from Nagihara et al. 2018


def ingest_nagihara_2018(
        spreadsheet_path="./source/nagihara/jgre.xlsx"
):
    nagihara_datafiles = ["a15_1975", "a17_1975", "a17_1976", "a17_1977"]

    # The 1975 data from this paper have been superseded by the related July
    # 2019 PDS release, so we only ingest the 1976 and 1977 data.
    nagihara_data = NestingDict()
    for worksheet_ix, mission in enumerate(nagihara_datafiles):
        if mission[4:] == "1975":
            # then the data have been superseded. move on.
            continue
        sheet = pd.read_excel(spreadsheet_path, worksheet_ix, header=0)
        for probe in ["p1", "p2"]:
            # The non-deprecated data from this paper is from the
            # upper gradient bridges of both Apollo 17 probes, so:
            sensor = 1

            # we initially read each 'file' (bridge) as a dict of
            # arrays for convenience.

            # Time
            # the original HFE dataset reduced time data into an
            # epoch time format as described above. Nagihara et al.
            # reduced time into days from the beginning of the
            # then-current calendar year and seconds from the
            # beginning of that day. This converts Nagihara et al.'s
            # time data into the format given in the original HFE
            # dataset.
            frame = {}
            column_indicator = ".1" if probe == "p2" else ""
            days = np.vectorize(days_since_year)(
                sheet["Day" + column_indicator],
                int(mission[-4:])
            )
            seconds = np.vectorize(seconds_interval)(
                sheet["Seconds" + column_indicator]
            )
            utc_time = days + seconds
            frame["Time"] = np.vectorize(a17_time)(
                np.vectorize(utc_to_tai)(utc_time)
            )
            # The original HFE dataset reduced temperature data into T and
            # dT, where T is the average temperature across the bridge and
            # dT is the difference between the upper and lower parts of the
            # bridge. Nagihara et al. reduced the ALSEP data differently,
            # explicitly giving temperature values for 'A' (upper) and 'B' (
            # lower) parts of the bridge. This converts Nagihara et al.'s
            # temperature data into the format given in the original HFE
            # dataset.

            TGA = sheet["TG" + probe[1] + str(sensor) + "A"]
            TGB = sheet["TG" + probe[1] + str(sensor) + "B"]
            frame["T"] = (TGA + TGB) / 2
            frame["dT"] = TGB - TGA
            # We also retain Nagihara et al.'s explicitly-computed bridge
            # values to avoid rounding errors later.
            frame["TG" + probe[1] + str(sensor) + "A"] = TGA
            frame["TG" + probe[1] + str(sensor) + "B"] = TGB

            # convert to pandas dataframes and drop empty rows. we don't
            # flag empty rows here because they're just formatting
            # artifacts. previous versions wrote intermediate csv files,
            # but we don't bother here; may add later if efficiency becomes
            # an issue or they prove desirable for some other reason.
            nagihara_data[mission][probe][sensor] = pd.DataFrame.from_dict(
                frame
            ).dropna()
    return nagihara_data


def ingest_nagihara_2019(nagihara_data=None, pathname="."):
    """
    grab files in directory according to Nagihara et al.'s naming convention
    and read them as pandas dataframes.
    """
    # These files can be interpreted as csv with fields separated by a variable
    # number of spaces
    # as elsewhere, m is mission (here mission by year), p is probe number,
    # s is 'file,' i.e. bridge identifier.

    missions = ["a15_1975", "a17_1975"]
    probes = ["p1", "p2"]
    sensors = [1, 2]
    for mission, probe, sensor in product(missions, probes, sensors):
        filename = "{pathname}/{m}_hfe_1975_l2_arcsav_tg{p}{s}.tab".format(
            pathname=pathname, m=mission[0:3], p=probe[1], s=sensor
        )
        if not os.path.isfile(filename):
            continue  # skipping gradient bridge files they didn't release

        frame = pd.read_csv(filename, engine="python", sep=r"\ +")

        # Time
        # generate a separate column for mission epoch time.
        # convert native DOY format (e.g. '1975-092T00:04:00.817')
        # to datetime as an intermediate step.

        # to_pydatetime is necessary because pandas otherwise gets mad
        # about loss of (here nonexistent) nanosecond precision.
        # then remove leap seconds for parity with NSSDC data and
        # convert to mission epoch time.
        frame["UTC_Time"] = np.vectorize(nagihara_doy_to_dt)(frame["time"])
        epoch_function = a15_time if mission[0:3] == "a15" else a17_time
        frame["Time"] = np.vectorize(
            epoch_function
        )(np.vectorize(tai_to_utc)(frame["UTC_Time"].dt.to_pydatetime()))
        frame.drop(columns=["time"], inplace=True)

        # dT
        # Nagihara et al. include both the high- and low-sensitivity dT
        # measurements for every data point. To construct our reduced sets,
        # we choose one of these measurements per point as a canonical dT;
        # specifically, we simply select the dT measurement that Nagihara
        # et al. used to calculate their canonical bridge temperatures.
        dT_init = frame["Time"].size
        frame["dT"] = pd.Series(np.zeros(dT_init))
        TA = frame["TG{p}{s}A".format(p=probe[1], s=sensor)]
        TB = frame["TG{p}{s}B".format(p=probe[1], s=sensor)]
        DTH = frame["DTH{p}{s}".format(p=probe[1], s=sensor)]
        DTL = frame["DTL{p}{s}".format(p=probe[1], s=sensor)]

        # is TA - TB within a rounding error of a given measurement?
        # then select that measurement as canonical dT, preferring DTH
        # if both measurements qualify.
        DTH_index = round(abs(TA - TB - DTH), 3) <= 0.01
        DTL_index = round(abs(TA - TB - DTL), 3) <= 0.01

        frame.loc[DTL_index, "dT"] = DTL.loc[DTL_index]
        frame.loc[DTH_index, "dT"] = DTH.loc[DTH_index]

        # are there points where neither measurement qualifies? something has
        # gone wrong with the analysis.

        if not np.all(np.bitwise_or(DTL_index, DTH_index)):
            raise ValueError(
                "Margin of error for PDS data dT selection appears to be off."
            )
        # then flip the sign for parity with the NSSDC convention
        frame["dT"] = (frame["dT"] * -1)

        # rename and reindex columns for parity with NSSDC data and later
        # convenience
        frame.rename(
            columns={"TG{p}{s}avg".format(p=probe[1], s=sensor): "T"},
            inplace=True,
        )
        frame = frame.reindex(
            columns=[
                "Time",
                "T",
                "dT",
                "UTC_Time",
                "TG{p}{s}A".format(p=probe[1], s=sensor),
                "TG{p}{s}B".format(p=probe[1], s=sensor),
            ]
        )

        # and place it into the dictionary
        nagihara_data[mission][probe][sensor] = frame

    return nagihara_data


# functions for polishing dataset and splitting to thermometers.


def discard_flagged(data):
    data_clean = pd.DataFrame(columns=data.columns)
    # retain ambiguous dT corrections and time inversions
    forbidden_flags = sum(
        [
            0b1,
            0b100,
            0b1000,
            0b10000,
            0b100000,
            0b1000000,
            0b10000000,
            0b100000000,
            0b1000000000,
        ]
    )
    index = np.bitwise_and(data["flags"], forbidden_flags).values == 0
    for column in data.columns:
        data_clean[column] = data[column].loc[index].values
    return data_clean


def substitute_corrections(data):
    if "dT_corr" in data.columns:
        data["dT"] = data["dT_corr"]
        data.drop(columns=["dT_corr"], inplace=True)


def standardize_time(data, mission):
    """
    place time into ISO 8601 scale / representation

    use directly-reformatted time from Nagihara; it's given to millisecond
    precision and meaningful floating-point errors could plausibly be
    introduced

    otherwise go ahead and do the full conversion from epoch time.
    """
    if "UTC_Time" in data.columns:
        data["Time"] = data["UTC_Time"]
        data.drop(columns=["UTC_Time"], inplace=True)
    elif mission[0:3] == "a17":
        data["Time"] = np.vectorize(a17_to_greg)(data["Time"])
        data["Time"] = np.vectorize(tai_to_utc)(data["Time"])
    elif mission[0:3] == "a15":
        data["Time"] = np.vectorize(a15_to_greg)(data["Time"])
        data["Time"] = np.vectorize(tai_to_utc)(data["Time"])


def polish_hfe(data):
    for mission, probe, sensor in tree_tuples(data):
        data[mission][probe][sensor] = discard_flagged(
            data[mission][probe][sensor]
        )
        substitute_corrections(data[mission][probe][sensor])
        standardize_time(data[mission][probe][sensor], mission)


def join_hfe_years(data):
    """
    just append nagihara data to the end of the nssdc data.
    """
    for mission in ["a15_1975", "a17_1975", "a17_1976", "a17_1977"]:
        for probe in data[mission]:
            for sensor in data[mission][probe]:
                data[mission[0:3]][probe][sensor] = (
                    data[mission[0:3]][probe][sensor]
                    .append(data[mission][probe][sensor])
                    .reset_index(drop=True)
                )
        del data[mission]


# standard expressions for each bridge by file number,
# as lists of bridge type / number
SENSOR_CODES = {
    1: ["G", "1"],
    2: ["G", "2"],
    4: ["R", "1"],
    5: ["R", "2"]
}


def split_to_thermometers(data):
    data_split = NestingDict()
    for mission, probe, sensor in tree_tuples(data):
        if mission[3:] == "":  # i.e., NSSDC data
            # construct per-thermometer temperature fields for NSSDC data
            probe_code = probe[1]
            if sensor != 3:
                sensor_code = SENSOR_CODES[sensor]
                A = "T" + sensor_code[0] + probe_code + sensor_code[1] + "A"
                B = "T" + sensor_code[0] + probe_code + sensor_code[1] + "B"
                frame = pd.DataFrame(columns=["Time", A, B])
                source = data[mission][probe][sensor]
                frame["Time"] = source["Time"]
                frame[A] = (source["T"] - 0.5 * source["dT"])
                frame[B] = (source["T"] + 0.5 * source["dT"])
                frame["flags"] = source["flags"]
            else:
                TC = "TC{p}".format(p=probe_code)
                frame = data[mission][probe][sensor] \
                    .copy() \
                    .drop("HTR", axis=1) \
                    .rename(
                    columns={
                        "TC1": TC + "1",
                        "TC2": TC + "2",
                        "TC3": TC + "3",
                        "TC4": TC + "4",
                        "TREF": "TREF",
                        "flags": "flags",
                    }
                )
            for column in frame:
                # round time back to second precision rather than the
                # microsecond precision introduced by astropy time scale
                # conversion.
                if column == "Time":
                    frame[column] = frame[column].dt.round("1s")
                # retains the (probably spurious) 5 digits after decimal given
                # by the Lamont data, rather than the (definitely spurious)
                # additional digits of precision introduced by Python's
                # floating point representation.
                elif column[0] == "T":
                    frame[column] = round(frame[column], 5)
        else:
            # simply use temperatures calculated by Nagihara et al. to avoid
            # introducing errors
            frame = data[mission][probe][sensor].copy().drop(
                columns=["T", "dT"]
            )
            for column in frame:
                # retain millikelvin precision of Nagihara et al. sets
                # rather than spurious precision introduced by numpy
                # floating point representation
                if column[0:2] == "TG":
                    frame[column] = round(frame[column], 3)
        data_split[mission][probe][sensor] = frame
    return data_split


# functions & depth dictionary for writing combined 'depth' set

# cm below surface for each sensor. 'S' marks sensors lying somewhere on the
# surface, 'N' marks the fourth thermocouple at the same position as the top
# gradient thermometer, 'X' marks off-scale bridges. the assembly functions
# for the third / depth set exclude these ranges from consideration; they
# are included for possible future work.

DEPTHDICT = {
    "a17": {
        "p1": {
            1: {"TG11A": 130, "TG11B": 177},
            2: {"TG12A": 185, "TG12B": 233},
            3: {"TC11": "S", "TC12": 14, "TC13": 66, "TC14": "N", "TREF": "S"},
            4: {"TR11A": 140, "TR11B": 167},
            5: {"TR12A": 195, "TR12B": 223},
        },
        "p2": {
            1: {"TG21A": 131, "TG21B": 178},
            2: {"TG22A": 186, "TG22B": 234},
            3: {"TC21": "S", "TC22": 15, "TC23": 67, "TC24": "N", "TREF": "S"},
            4: {"TR21A": 140, "TR21B": 169},
            5: {"TR22A": 196, "TR22B": 224},
        },
    },
    "a15": {
        "p1": {
            1: {"TG11A": 35, "TG11B": 84},
            2: {"TG12A": 91, "TG12B": 139},
            3: {"TC11": "S", "TC12": "S", "TC13": 0, "TC14": "N", "TREF": "S"},
            4: {"TR11A": 45, "TR11B": 73},
            5: {"TR12A": 101, "TR12B": 129},
        },
        "p2": {
            1: {"TG21A": [-6, "X"], "TG21B": [32, "X"]},
            2: {"TG22A": 49, "TG22B": 97},
            3: {"TC21": "S", "TC22": "S", "TC23": "S", "TC24": 0, "TREF": "S"},
            4: {"TR21A": [3, "X"], "TR21B": [41, "X"]},
            5: {"TR22A": 59, "TR22B": 87},
        },
    },
}


def combine_with_depth(data):
    """
    concatenates all subsurface sensors (barring TC4) per probe
    and assigns depth values.
    """
    data_depth = NestingDict()
    for mission, probe in product(["a15", "a17"], ["p1", "p2"]):
        data_depth[mission][probe] = pd.DataFrame(
            columns=["Time", "T", "sensor", "depth", "flags"]
        )
    for mission, probe, sensor in base_hfe_filenames():
        for column in data[mission][probe][sensor].columns:
            # is it a temperature value? i.e., a temperature, not 'Time'
            if not ((column[0] == "T") and (column[1] != "i")):
                continue
            # is it below-surface?
            if not (
                    isinstance(DEPTHDICT[mission][probe][sensor][column], int)
                    and DEPTHDICT[mission][probe][sensor][column] > 0
            ):
                continue
            depth_slice = data[mission][probe][sensor][
                ["Time", column, "flags"]
            ].copy()
            depth_slice = depth_slice.reindex(
                ["Time", "T", column, "sensor", "depth", "flags"],
                axis=1,
            )
            depth_slice["depth"] = DEPTHDICT[mission][probe][sensor][column]
            depth_slice["sensor"] = column
            depth_slice["T"] = depth_slice[column]
            depth_slice = depth_slice.drop(column, axis=1)
            data_depth[mission][probe] = data_depth[mission][probe] \
                .append(depth_slice)
    for mission, probe in product(["a15", "a17"], ["p1", "p2"]):
        data_depth[mission][probe] = data_depth[mission][probe] \
            .sort_values(by="Time").reset_index(drop=True)
    return data_depth
