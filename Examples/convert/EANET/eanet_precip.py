#!/usr/bin/env python
# coding=utf-8
"""
Convert EANET precip measurements files to ebas
"""

import datetime
import logging
import sys
from ebas.commandline import EbasCommandline
from ebas.io.fileset import EbasIOResultSet
from ebas.io.file.eanet import EbasEanetPrecip, EbasEanetReadError

VERSION = '0.01.00'
VERSION_DATE = datetime.datetime(2021, 10, 13)


def add_private_args(parser, ebascmdline):  # @UnusedVariable
    # pylint: disable=W0613
    # W0613 Unused argument
    """
    Callback function for commandline.getargs(). Adds private commandline
    arguments.

    Parameters:
        parser       root parser object from commandline.getargs()
        ebascmdline  ebas commandline object
    Returns:
        None
    """
    parser_input_group = parser.add_argument_group('input options')
    parser_input_group.add_argument(
        'filenames', nargs='*',
        help='input file(s), NOAA NMHC flask file format')

def eanet_precip(cmdline):
    """
    Main program. Entry point and callback from EbasCommandline.
    """
    logger = logging.getLogger('eanet_precip')
    args = cmdline.args
    input_options = cmdline.get_custom_args('OTHER_READ')
    output_options = cmdline.get_custom_args('FILE_OUTPUT')
    files = 0
    errors = 0
    warnings = 0
    errfiles = 0
    okfiles = 0
    fileset = EbasIOResultSet(**output_options)

    for filename in args.filenames:
        files += 1
        infil = EbasEanetPrecip(**input_options['file_init'])
        try:
            infil.read(filename, **input_options['file_read'])
        except (IOError, EbasEanetReadError) as excpt:
            logger.error("%s: %s", filename, str(excpt))
            errors += infil.errors
            warnings += infil.warnings
            errfiles += 1
            continue
        errors += infil.errors
        warnings += infil.warnings
        okfiles += 1
        fileset.add_ebasfile(infil)

    fileset.extract_all()
    if errors or errfiles:
        logger.error(
            "%d files processed, %d files OK, %d files failed, %d errors, "
            "%d warnings", files, okfiles, errfiles, errors, warnings)
    else:
        logger.info(
            "%d files processed, %d files OK, %d files failed, %d errors, "
            "%d warnings", files, okfiles, errfiles, errors, warnings)
    exitcode = min(255, errfiles)
    sys.exit(exitcode)


# pylint: disable=invalid-name
# (app and year are not constants, and should not be upper case...)
app = EbasCommandline(
    eanet_precip,
    custom_args=['CONFIG', 'LOGGING', 'OTHER_READ', 'FILE_OUTPUT'],
    private_args=add_private_args,
    help_description='%(prog)s convert data from EANET precip files to EBAS',
    version=VERSION, version_date=VERSION_DATE)
app.run()
