#!/usr/bin/env python
"""
$Id: ebas_flatcsv.py 1369 2016-09-01 14:02:07Z pe $

Example for reading an EBAS_1.1 NasaAmes datafile.
"""
import sys
import logging
import csv
from ebas.commandline import EbasCommandline
from ebas.io.file import nasa_ames

__version__ = '1.00.00'

def add_private_args(parser, cmdline):  # pylint: disable=W0613
    # W0613: Unused argument 'cmdline'
    """
    Callback function for commandline.getargs(). Adds private commandline
    arguments.

    Parameters:
        parser    root parser object from commandline.getargs()
        cmdline   EbasCommandline object (may be needed for some private args)
    Returns:
        None
    """
    parser_input_group = parser.add_argument_group('input options')
    parser_input_group.add_argument('--skip_unitconvert', action='store_true')
    parser_input_group.add_argument('--ignore_parameter', action='store_true')
    parser_input_group.add_argument(
        'filenames', nargs='*',
        help='input file(s), EBAS NASA-Ames format')

def prepare_csv():
    """
    Prepares the csv file for output (create file, setup csv object, add header)
    Parameters:
        None
    Returns:
        csv.writer object
    """
    outfile = open("output.csv", "w")
    csv.register_dialect('ebas', delimiter=',', quotechar='"')
    csvwriter = csv.writer(outfile, dialect='ebas', quoting=csv.QUOTE_MINIMAL)
    header = ["Set type code",
              "Timezone",
              "Period code",
              "Resolution code",
              "Station code",
              "Platform code",
              "Station name",
              "Station latitude",
              "Station longitude",
              "Station altitude",
              "Instrument type",
              "Laboratory code",
              "Instrument name",
              "Method ref",
              "Regime",
              "Matrix",
              "Component",
              "Statistics",
              "Unit",
              "Start time",
              "End time",
              "Value",
              "Flags"]
    csvwriter.writerow(header)
    return csvwriter

def csv_rows(nas):
    """
    Create output rows for csv output.
    Parameters:
        nas     EbasNasaAmes object (input file)
    Returns:
        generator (rows (each row is a list with column data))
    """
    for vnum in range(len(nas.variables)):
        row = [nas.get_meta_for_var(vnum, 'type'),
               nas.get_meta_for_var(vnum, 'timezone'),
               nas.get_meta_for_var(vnum, 'period'),
               nas.get_meta_for_var(vnum, 'resolution'),
               nas.get_meta_for_var(vnum, 'station_code'),
               nas.get_meta_for_var(vnum, 'platform_code'),
               nas.get_meta_for_var(vnum, 'station_name'),
               nas.get_meta_for_var(vnum, 'station_latitude'),
               nas.get_meta_for_var(vnum, 'station_longitude'),
               nas.get_meta_for_var(vnum, 'station_altitude'),
               nas.get_meta_for_var(vnum, 'instr_type'),
               nas.get_meta_for_var(vnum, 'lab_code'),
               nas.get_meta_for_var(vnum, 'instr_name'),
               nas.get_meta_for_var(vnum, 'method'),
               nas.get_meta_for_var(vnum, 'regime'),
               nas.get_meta_for_var(vnum, 'matrix'),
               nas.get_meta_for_var(vnum, 'comp_name'),
               nas.get_meta_for_var(vnum, 'statistics'),
               nas.get_meta_for_var(vnum, 'unit')]
        for tim in range(len(nas.sample_times)):
            yield row + \
               [nas.sample_times[tim][0],
                nas.sample_times[tim][1],
                nas.variables[vnum].values_[tim],
                nas.variables[vnum].flags[tim]]

def ebas_flatcsv(cmdline):
    """
    Main program for ebas_flatcsv
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_flatcsv')
    args = cmdline.args

    csvwriter = prepare_csv()

    exitcode = 0 # number of failed files (max 255)
    for filename in args.filenames:
        nas = read_file(args, logger, filename)
        if nas is None:
            exitcode += 1
        else:
            for row in csv_rows(nas):
                csvwriter.writerow(row)
            logger.info(
                '%d variables with %d sammples exported',
                len(nas.variables), len(nas.sample_times))
    exitcode = min(255, exitcode)
    sys.exit(exitcode)

def read_file(args, logger, filename):
    """
    Reads a single file.
    Parameters:
        args      commandline arguments
        logger    logger object
        filename  filename (including path) of file to be read
    Returns:
        EbasNasaAmes file object or None in case of erros.
    """
    logger.info('reading input file {}'.format(filename))
    nas = nasa_ames.EbasNasaAmes()
    try:
        nas.read(filename, skip_unitconvert=args.skip_unitconvert,
                 ignore_parameter=args.ignore_parameter)
    except (IOError, nasa_ames.EbasNasaAmesReadError) as excpt:
        logger.error("file {}: {}".format(filename, str(excpt)))
        return None
    return nas

EbasCommandline(
    ebas_flatcsv,
    custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT'],
    private_args=add_private_args,
    help_description='%(prog)s example for reading a NasaAmes datafile.',
    version=__version__).run()
