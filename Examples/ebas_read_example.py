#!/usr/bin/env python
"""
$Id: ebas_read_example.py 1737 2017-07-14 13:36:19Z pe $

Example for reading an EBAS_1.1 NasaAmes datafile.
"""
import sys
import logging
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
    Returns:
        None
    """
    parser_input_group = parser.add_argument_group('input options')
    parser_input_group.add_argument(
        'filenames', nargs='*', help='input file(s), EBAS NASA-Ames format')

def ebas_read_example(cmdline):
    """
    Main program for ebas_read_example
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_read_example')
    args = cmdline.args

    exitcode = 0 # number of failed files (max 255)
    for filename in args.filenames:
        nas = read_file(cmdline, logger, filename)
        if nas is None:
            exitcode += 1
        else:
            use_file_example(nas, args.time)
    exitcode = min(255, exitcode)
    sys.exit(exitcode)

def read_file(cmdline, logger, filename):
    """
    Reads a single file.
    Parameters:
        cmdline   EbasCommandline object (wrapper)
        logger    logger object
        filename  filename (including path) of file to be read
    Returns:
        EbasNasaAmes file object or None in case of erros.
    """
    nas = nasa_ames.EbasNasaAmes()
    nas_opt = cmdline.get_custom_args('NASA_READ')
    try:
        nas.read(filename, **nas_opt['nas_read'])
    except (IOError, nasa_ames.EbasNasaAmesReadError) as excpt:
        logger.error("file {}: {}".format(filename, str(excpt)))
        return None
    return nas

def use_file_example(nas, time):
    """
    Example for usage of an i/o object after reading it from file.
    Prints some extracted data to stdout.
    Parameters:
        nas    nasa ames i/o object
        time   time interval for printing values
    Returns:
        None
    """
    # print info about the tile axis:
    time_index = nas.find_sample_time_index(time)
    if time_index:
        print(("\nfound {} samples for time criteria ({}):".format(
            (time_index[1]-time_index[0]+1), time)))
        for tim in range(time_index[0], time_index[1]+1):
            print((" {} - {}".format(nas.sample_times[tim][0],
                                     nas.sample_times[tim][1])))
    else:
        print("\nno sample time found for time criteria ({})".format(time))

    # print info about variables:
    for i in range(len(nas.variables)):
        print("\nVariable {}: {}".format(i+1, nas.vname(i)[0]))
        vmeta = nas.metadata.copy()
        vmeta.update(nas.variables[i].metadata)
        print("   all metadata for variable: {}".format(vmeta))

    if nas.variables:
        print("Example data handling, first variable: {}".format(nas.vname(0)[0]))

        if time_index:
            print("\n  example output for time and variable (including flags):")
            for tim in range(time_index[0], time_index[1]+1):
                print(("   {} - {}, value={}, flags={}".format(
                    nas.sample_times[tim][0],
                    nas.sample_times[tim][1],
                    nas.variables[0].values_[tim],
                    nas.variables[0].flags[tim])))
            print ("\n  example output for time and variable (w/o flags - "
                   "valid values only):")
            for tim in range(time_index[0], time_index[1]+1):
                print(("   {} - {}, value={}".format(
                    nas.sample_times[tim][0], nas.sample_times[tim][1],
                    nas.values_without_flags(0)[tim])))

    # look for specific variable
    # PCB_118,Statistics=arithmetic mean
    for i in nas.find_variables({'comp_name': 'PCB_118',
                                 'statistics': 'arithmetic mean'}):
        print(('\n found variable PCB_118, Statistics=arithmetic mean: '
               'var_index={}'.format(i)))

    # look for specific variable
    # ozone, in nmol/mol
    for i in nas.find_variables({'comp_name': 'ozone',
                                 'unit': 'nmol/mol'}):
        print(('\n found variable ozone, nmol/mol: '
               'var_index={}'.format(i)))
    # ozone, in ug/m3
    for i in nas.find_variables({'comp_name': 'ozone',
                                 'unit': 'ug/m3'}):
        print(('\n found variable ozone, ug/m3: '
               'var_index={}'.format(i)))

    # ec/oc find variable witth Fraction=OC2
    for i in nas.find_variables({
            'comp_name': 'organic_carbon',
            'characteristics': {'Fraction': 'OC2'}}):
        print(('\n found variable organic_carbon, Fraction=OC2: '
               'var_index={}'.format(i)))
    # ec/oc find all variable where characteristics Fraction is set
    # (no matter which value)
    for i in nas.find_variables({
            'comp_name': 'organic_carbon',
            'characteristics': {'Fraction': True}}):
        print(('\n found variable organic_carbon, with any Fraction: '
               'var_index={}'.format(i)))
    # ec/oc find variable organic_carbon, arithmetic mean, without a characteristic
    # Fraction or Artifact specified
    for i in nas.find_variables({
            'comp_name': 'organic_carbon',
            'statistics': 'arithmetic mean',
            'characteristics': {'Fraction': False, 'Artifact': False}}):
        print(('\n found variable organic_carbon, arithmetic mean, without '
               'any Fraction or Artifact: var_index={}'.format(i)))

                                 
EbasCommandline(
    ebas_read_example,
    custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT', 'NASA_READ'],
    private_args=add_private_args,
    help_description='%(prog)s example for reading a NasaAmes datafile.',
    version=__version__).run()
