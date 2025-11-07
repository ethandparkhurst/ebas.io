********
Metadata
********

Metadata are provided at different levels (global attributes, variable
attributes and variables containing metadata for specific time ranges).

Metadata can be required or recommended by different metadata convention.
Additionally, the full set of EBAS metadata is provided at the different levels.

Metadata governed by mentioned conventions are on a more generic an higher level.
Those metadata are particularly useful for data discovery, visualisation or processing in a more generic way.
They are very important to make standard tools work seamlessly with EBAS NetCDF files.

EBAS metadata are more detailed and very specific to the various types of measurement.

Supported Metadata Conventions
==============================

NetCDF
------

The `NetCDF Users Guide <https://docs.unidata.ucar.edu/nug/current/index.html>`_
recommends the global attributes ``title``, ``history`` and ``Conventions``
as well as the variable attribute ``long_name`` and ``unit`` for all variables.

CF Metadata Conventions
-----------------------

The `CF Metadata Conventions <https://cfconventions.org>`_ 
requires a longer list of metadata as global or variable attributes as well as
some additional concepts, like :ref:`boundary variables<time_bnds>`.


ACDD convention
---------------

The `ACDD convention <https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery>`_
focuses on attributes recommended for describing netCDF datasets to discovery systems.
Cataloging tools like the THREDDS can use this metadata or map to other metadata
standards (Dublin Core, ISO 19115).

EBAS Metadata
=============

:ref:`All EBAS metadata<all_ebasmetadata>` are supported and used in EBAS NetCDF files. 

Metadata will appear in three different places:

 * **As global attributes:** EBAS metadata will appear as global attributes when:

   * The respective metadata element is the same for all variables and the full time ranges in the file.
     This is typically the case for common metadata like e.g. station and instrument metadata.

   * For some metadata elements an aggregation of metadata in the file is useful.
     This is the case for framework, originator (PI) and submitter as well as revision date.

   EBAS metadata are implemented as global attributes with the prefix ``ebas_``.
   The attribute names of all possible EBAS metadata can be seen in the column
   *NetCDF Tag* in this :ref:`list<all_ebasmetadata>`

   Example:  global attribute ``ebas_data_definition``.

 * **As variable attributes:** EBAS metadata will appear as variable attributes when
   the metadata value applies to the whole time range of the variable.
   EBAS metadata are variable attribues with the prefix ``ebas_``.
   The attribute names of all possible EBAS metadata can be seen in the column
   *NetCDF Tag* in this :ref:`list<all_ebasmetadata>`

 * **As time dependent metadata:** Some metadata may change over time during the valid period
   of the dataset. As an example, the instrument serial number might change during
   many years of measurement. More on time dependent metadata in the next paragraph.

.. toctree::
 
   gen_ebas_metadata.rst


.. _time_dependent_metadata:

Time depenendent EBAS metadata
------------------------------

As mentioned above, some metadata in EBAS can change over time. For file formats like
the EBAS Nasa Ames file format, this means that a files need to be split on every change
of metadata during history.

One of the biggest technical advantage of the EBAS NetCDF fileformat is that those
metadata changes can be stored in the file. Thus, all datasets (DOIs) in EBAS
can be written to a single NetCDF file.

Time dependent metadata are implemented as an additional variable for **each data
variable**, see :ref:`metadata_variable`

There is a dedicated time dimension for all metadata changes, called :ref:``metadata_time<dim_metadata_time>``.
This should not be confused with the ``time`` dimension used for the measurement data.
The ``time`` dimension has usually a length of > 1000 (one for each measurement interval),
the ``metadata_time`` dimension has typically only a length of < 10, one for each change of metadata.


