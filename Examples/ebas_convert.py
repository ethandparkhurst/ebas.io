#!/usr/bin/env python
"""
$Id: ebas_convert.py 2721 2021-10-22 23:02:49Z pe $

Example for reading an EBAS_1.1 NasaAmes datafile and writing the same file
in a different file format.
"""
import sys
import logging
import argparse
import textwrap
import re
from nilutility.argparse_helper import ParseStrings, ParseIntegers
from ebas.commandline import EbasCommandline
from ebas.io.file import EBAS_IOSTYLE_KEEP
from ebas.io.file.nasa_ames import EbasNasaAmes, EbasNasaAmesReadError
from ebas.io.fileset import EbasIOResultSet
from ebas.io.file.base import EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV, \
    EBAS_IOFORMAT_XML, EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_OPENDAP
__version__ = '1.00.00'

class ParseDestDirAction(argparse.Action):  # pylint: disable-msg=R0903
    # R0903: ParseDestDirAction: Too few public methods
    #  this is due to argparse.Action
    """
    Parser action for --destdir argument: is only allowed when --createfiles is
    set.
    """
    def __call__(self, parser, namespace, values, _option_string=None):
        createfiles = getattr(namespace, 'createfiles', False)
        if createfiles == False:
            parser.error("--destdir is only allowed after --createfiles!")
        else:
            setattr(namespace, self.dest, values)


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
    parser_nasa_group = parser.add_argument_group('nasa ames reading options')
    parser_nasa_group.add_argument(
        'filenames', nargs='*',
        help='input file(s), EBAS NASA-Ames format')

def ebas_convert(cmdline):
    """
    Main program for ebas_convert
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_convert')
    args = cmdline.args
    nas_opt = cmdline.get_custom_args('NASA_READ')
    output_options = cmdline.get_custom_args('FILE_OUTPUT')

    exitcode = 0 # number of failed files (max 255)

    fileset = EbasIOResultSet(**output_options)

    for filename in args.filenames:
        nas = read_file(nas_opt, logger, filename)
        if nas is None:
            exitcode += 1
        else:
            fileset.add_ebasfile(nas)
    fileset.extract_all()
    exitcode = min(255, exitcode)
    sys.exit(exitcode)

def read_file(nas_opt, logger, filename):
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

    nas = EbasNasaAmes(**nas_opt['nas_init'])

    try:
        nas.read(filename, **nas_opt['nas_read'])
    except (IOError, EbasNasaAmesReadError) as excpt:
        logger.error("file {}: {}".format(filename, str(excpt)))
        return None
    return nas

EbasCommandline(
    ebas_convert,
    custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT', 'NASA_READ',
                 'FILE_OUTPUT_KEEPCOLUMNS'],
    private_args=add_private_args,
    help_description='%(prog)s example for converting a NasaAmes datafile to '
    'different dataformats', version=__version__).run()
