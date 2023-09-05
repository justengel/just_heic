=========
just_heic
=========

Convert heic files to jpg files fixing orientation and preserving date times.


.. code-block:: python

    just_heic to_jpg file.heic file.jpg
    just_heic to_jpg src_folder dest_folder -r -t -v
    just_heic to_jpg --help


Change created time to the exif metadata date taken.

.. code-block:: python

    just_heic to_date_taken src_folder -r --ext .jpg
    just_heic to_date_taken --help


Install
=======

.. code-block::

    pip install just_heic