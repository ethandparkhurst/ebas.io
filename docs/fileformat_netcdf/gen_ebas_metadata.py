from gen_temp_ascii import get_link
from ebas.io.ebasmetadata import EbasMetadata, EBAS_IOFORMAT_NASA_AMES
meta = EbasMetadata('EBAS_1.1', EBAS_IOFORMAT_NASA_AMES, data_level='0')

with open('gen_ebas_metadata.rst', 'w') as fil:
    fil.write("""
.. _all_ebasmetadata:

*************************
List of all EBAS Metadata
*************************

.. list-table:: Title
   :header-rows: 1

   * - Nasa Ames tag
     - NetCDF Tag
""")

    for elem in [x for x in meta.metadata if x['main'] or x['vname']]:
        if not 'renamed_tag' in elem:
            lnk = get_link(elem["tag"], '')
            if lnk == 'yet_to_come':
                lnk = None
            else:
                lnk = 'https://ebas-submit.nilu.no/templates/comments/' + lnk
            if lnk:
                fil.write(f'   * - `{elem["tag"]} <{lnk}>`_\n')
                fil.write(f'     - `ebas_{elem["nc_tag"]} <{lnk}>`_\n')
            else:
                fil.write(f'   * - {elem["tag"]}\n')
                fil.write(f'     - ebas_{elem["nc_tag"]}\n')

