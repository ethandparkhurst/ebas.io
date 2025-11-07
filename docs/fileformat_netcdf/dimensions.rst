**********
Dimensions
**********

Main dimensions
===============

The following dimensions are present in every EBAS NetCDF file:

 * ``time``: time dimension for measurement data
 * ``metadata_time``: time dimension for metadata
 * ``tbnds``: addirional dimension for :ref:``time boundary variables<time_bnds>``
 * For each data variable, there will be a dimension for the different flags
   used in the flag variable.
 * Additional dimensions for multidimensional variables
 
.. _dim_time:

time
----

The ``time`` dimension represents the time ranges for all measurements in the time
series of all data variables.

All data variables share the same time dimension and thus contain the same
measurement intervals.

The ``time`` variable is, following the CF convention defined as follows::

   standard_name: time
   long_name: time of measurement
   units: days since 1900-01-01 00:00:00 UTC
   axis: T
   calendar: gregorian
   bounds: time_bnds

Following the CF convention the time variable is defined with the standard name ``time``
and uses a supported unit specification. CF also requires the calendar attribute and
recommends the bounds attribute. More on the :ref:`time_bnds` can be found below.

.. _dim_metadata_time:

metadata_time
-------------

The dimension ``metadata_time`` is used for :ref:`time_dependent_metadata`.

.. _time_bnds:

Time boundaries
---------------

The variables ``time`` and ``metadata_time`` associated with the main dimensions of
the EBAS NetCDF files contain only timestamps (point in time).

In reality, measurements are performed over a certain time range (e.g. one hour).
Thus, each measurement has a start and an end time.

The CF convention defines for this problem the concept of
`boundary variables <http://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#cell-boundaries>`_.

The time axis values (in the ``time`` variable) are set to the midpoint of the
time ranges for all measuremnts. The additional variable ``time_bnds`` contains
one more dimension (``tbnds``, length 2) an thus specifies starttime and endtime
of each measurement.

In analogy, the dimension variabl ``metadata_time`` contains a single timestamp
(midtime) for each time range with a distinct set of metadata. The associated
boundary variable ``metadata_time_bnds`` contains an additional dimension
``tbnds`` (length 2), which contains start- and end times for each metadata
validity period.


.. _dim_additional:

Additional dimensions
=====================

Some parameters in EBAS have additional dimensions, the most prominent are:

.. list-table:: 
   :header-rows: 1

   * - Dimension
     - Description, applies to, example
   * - Wavelength
     - For variable which are measured in multiple wavelength, e.g.
       aerosol_light_scattering_coefficient (nepehlometer), aerosol_absorption_coefficient (filter_absorption_photometer),
       aerosol_optical_depth (sun_tracking_filter_radiometer).
   * - Wavelength min, Wavelength max
     - Same as above, but the wavelengths are specified as max and min, thus adding two additional dimenstions.
   * - Wavelength 1, Wavelength 2
     - For aerosol_absorption_angstrom_exponent calculated between two wavenelgths.
   * - D
     - Particle diameter (size bins), e.g, for particle_number_size_distribution.
   * - Dmin, Dmax
     - Same as above, but the size bins are defined with an upper and lower size, thus adding two additional dimenstions.
   * - Tower inlet height
     - Tower measurements performed in different heights.
   * - Profile height
     - aerosol_extinction_coefficient (maxdoas)
   * - RH, RH base, RH base max, RH humidified
     - aerosol_light_(back)scattering_coefficient as a function of rH.
   * - SS
     - Supersaturaion (%), for cloud_condensation_nuclei_number_concentration
   * - Location
     - Location of measurements, used for auxiliary data. E.g. temperature, pressure or humidity measured at different points in the sample line.
       E.g. temperature, Location=inlet; temperature, Location=instrument inlet; temperature, Location=instrument internal; temperature, Location=sheath air loop

.. _dim_flag:

Flag dimensions
===============

Each data variable is accompanied by a variable containing flag information.
This flag variable has the same dimensions as the measurement variable, plus one
additional dimension (``<variable name>_qc_flags``) for the flags which are
associated with each single measurement.
The length of this additional dimension is equal the maximum number of flags attached to a single measurement in the file.
More information on this in :ref:`flag_variable`.

