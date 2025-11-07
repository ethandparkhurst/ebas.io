#!/usr/bin/env python
"""
$Id: ebas_reformat.py 1737 2017-07-14 13:36:19Z pe $

Example for reading an EBAS_1.1 NasaAmes datafile and writing the same file
again, in order to stadardize the file format.
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

def ebas_reformat(cmdline):
    """
    Main program for ebas_reformat
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_reformat')
    args = cmdline.args

    exitcode = 0 # number of failed files (max 255)
    for filename in args.filenames:
        nas = read_file(args, logger, filename)
        if nas is None:
            exitcode += 1
        else:
            nas.write(createfiles=True)
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
                 ignore_parameter=args.ignore_parameter,
                 ignore_dx0=True)
    except (IOError, nasa_ames.EbasNasaAmesReadError) as excpt:
        logger.error("file {}: {}".format(filename, str(excpt)))
        return None
    return nas

EbasCommandline(
    ebas_reformat,
    custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT'],
    private_args=add_private_args,
    help_description='%(prog)s example for reformatting a NasaAmes datafile.',
    version=__version__).run()
