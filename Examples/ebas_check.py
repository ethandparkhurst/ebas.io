#!/usr/bin/env python
"""
ebas_check

Check an EBAS NasaAmes file.
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

def ebas_check(cmdline):
    """
    Main program for ebas_check
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_check')
    args = cmdline.args

    exitcode = 0 # number of failed files (max 255)
    for filename in args.filenames:
        nas = read_file(cmdline, logger, filename)
        if nas is None:
            exitcode += 1
    logger.info('checked {} files, {} failed, {} succeeded'.format(
        len(args.filenames), exitcode, len(args.filenames)-exitcode))
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
    except IOError as excpt:
        # IOError needs to be logged as error (no message logged before)
        # filename is included in IOError message text
        logger.error(str(excpt))
        return None
    except nasa_ames.EbasNasaAmesReadError as excpt:
        # EbasNasaAmesReadError message contains just the summary
        # (# errors, # warnings), the reason (errors have been logged before)
        # thus we need just info level here.
        logger.info("file {}: {}".format(filename, str(excpt)))
        return None
    logger.info("file {}: {} Errors, {} Warnings".format(filename, nas.errors,
                                                         nas.warnings))
    return nas

EbasCommandline(
    ebas_check,
    custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT', 'NASA_READ'],
    private_args=add_private_args,
    help_description='%(prog)s example for checking a NasaAmes datafile.',
    version=__version__).run()
