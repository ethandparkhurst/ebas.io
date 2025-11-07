######################
EBAS NetCDF Fileformat
######################


************
Introduction
************

The EBAS NetCDF file format features some advantages over the older EBAS
NasaAmes file format:

 * NetCDF/CF conformity
 * Good file access support by standard reading libraries
 * Datasets with changing metadata over time can be stored (see :ref:`time_dependent_metadata`)
 * Additional dimensions available for e.g. measurements in multiple size bins, wavenlength etc.

.. toctree::
   :maxdepth: 1
 
   metadata.rst
   dimensions.rst
   variables.rst
   examples.rst
