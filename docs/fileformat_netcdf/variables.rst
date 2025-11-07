*********
Variables
*********

Dimension Variables
===================

Some special variables have already been mentioned before when describing dimensions:

   * :ref:`time<dim_time>` and time_bnds for the measurement and time dimension
   * :ref:`metadata_time<dim_metadata_time>` and metadata_time_bnds for the metadata time dimension
   * :ref:`dim_additional` like Wavelength, D (particle diameter), Tower inlet height, etc.
   * :ref:`dim_flag`


Data variables
==============

Each data variable in EBAS is represented by three NetCDF variables:

   * :ref:`measurement variable`: The main variable containing the measurement values. Dimensions: :ref:`dim_time`, optional: :ref:`dim_additional`
   * :ref:`flag_variable`: an additional variable containing the flag information for the variable. Dimensions: same as measurements + :ref:`dim_flag`
   * :ref:`metadata_variable`: a variable for changing metadata over time

.. _measurement variable:

Measurement variable
--------------------

This is the main variable, containing the measurement values for an EBAS variable.
The name for measurement variables is described :ref:`here<variable names>`.

The dimensions are:

   * :ref`dim_time`
   * optional: :ref:`dim_additional`

The data type is ``double``.

Variable Attributes
^^^^^^^^^^^^^^^^^^^

The variable attributes contain the full set of EBAS metadata (constant over time
for the variable). But the most important attributes for understanding the content of the variable are:

 * ``cell_methods`` and ``ebas_statistics`` give information about the statistical interpretation (e.g. arithmetic mean, percentile:15.87, ...)
 * ``ebas_component``: Component name in EBAS
 * ``ebas_matrix``: Matrix name in EBAS
 * ``units`` and ``ebas_unit``: Unit of the measurements
 * ``ancillary_variables``: reference to the associated :ref:`flag_variable` and :ref:`metadata_variable`


.. _flag_variable:

Flag variable
-------------

For each measurement variable a related flag variable is added which contains the flag information for the measurements.
Flag variable are named like the measurement variable plus a postfix ``_qc``.

The dimensions are:

   * Same dimensions as the measurement variable
   * An additional :ref:`flag dimension<dim_flag>` called ``<variable name>__qc_flags``

The data type is ``int``.


.. _metadata_variable:

Metadata variable
-----------------

This additional variable implements :ref:`time_dependent_metadata`.
It contains metadata which change over time. This variable is
provided for each data variable.
The metadata variables are named like the main variable with a postfix ``_ebasmetadata``.

The dimensions are:

   * :ref:`dim_metadata_time`
     the length of the dimension is 1 for static metadata and n + 1 for each metadata change over time within the file


The data type for the metadata variables is string and it contains a set of all ebas
metadata for the specific time range as json encoded string.


Distinguishing Measurement variables, Flag variables and Metadata variables
---------------------------------------------------------------------------

   * Only the measurement variable has EBAS metadtaa as variable attributes
   * Only the measurement variable has a variable attributes ``_metadata_variable`` with references to the associated flag variable and metadata variable

   * The name of flag variables always ends with ``_qc`` (same name as measurement variable + ``_qc``)
   * The variable attribute ``standard_name`` is set to``status_flag``

   * The name of metadata variables always ends with ``_ebasmetadata`` (same name as measurement variable + ``_ebasmetadata``)


.. _variable names:

Variable names
--------------

Flag variables and metadata variables always use the same name as the measurement variables
plus a specific postfix (``_qc`` and ``_ebasmetadata`` respectively).

The name for measurement variables is not straight forward, and may vary in
different files depending on other variables in the file and related name conflicts.

   #. Generally, the variable name will be set to the ``ebas_component`` name
   #. If there are name conflicts (variables with an identical name) and one or
      more of the following metadata distinguish the variables with identical names:

        * matrix
        * unit
        * statistics
        * additional dimensions

    The respective element will be added to the name of all conflicting variables.

Example 1:
^^^^^^^^^^

A file contains three variables with component name ``aerosol_light_scattering_coefficient_amean``,
one with ``ebas_statistics=arithmetic mean``, one with ``ebas_statistics=percentile:15.87`` and one with ``ebas_statistics=percentile:84.13``

The variables can be destinguished by adding information about the ebas_statistics to their name. Solution: The three variables will be called:

   * ``aerosol_light_scattering_coefficient_amean``
   * ``aerosol_light_scattering_coefficient_prec1587`` and
   * ``aerosol_light_scattering_coefficient_prec8413``.

And each of those variables will be accompanied by their ``_qc`` and ``_ebasmetadata`` variable (total 9 variables).

Example 2:
^^^^^^^^^^

A file contains ``ozone`` measurement both in the EBAS default unit ``ug/m3`` and in a converted variable in ``nmol/mol``. Both are present as ``ebas_statistics=arithmetic mean``, ``ebas_statistics=min``, ``ebas_statistics=max`` and ``ebas_statistics=stddev``.

The variables can only be distinguished by adding information on both the unit and the ebas_statistics to their names. Solution: The eight variables will be called:

   * ``ozone_ug_per_m3_amean``
   * ``ozone_ug_per_m3_min``
   * ``ozone_ug_per_m3_max``
   * ``ozone_ug_per_m3_stddev``
   * ``ozone_nmol_per_mol_amean``
   * ``ozone_nmol_per_mol_min``
   * ``ozone_nmol_per_mol_max`` and 
   * ``ozone_nmol_per_mol_stddev``

And each of those variables will be accompanied by their ``_qc`` and ``_ebasmetadata`` variable (total 24 variables).

.. warning::
   Never rely on variable names. As shown above, they might vary from file to file.

   In order to find measurement variables in a file, use the variable attributes!

   For example, search for a variable with the following combination of attributes:

      * ``ebas_component=ozone``
      * ``ebas_statistics=arithmetic mean``
      * ``ebas_unit=nmol/mol``

