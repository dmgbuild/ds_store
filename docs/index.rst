.. ds_store documentation master file, created by
   sphinx-quickstart on Thu Feb 13 08:04:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ds_store - Manipulate Finder ``.DS_Store`` files from Python
============================================================

This document refers to version |release|

What is this?
=============

Historically the Mac OS Finder stored additional per-file information in a
special Finder Info field in the HFS/HFS+ filesystem.  It also held other
information in a single file known as the Desktop Database.

Filesystems other than HFS obviously do not have the Finder Info structure,
and until recently support for extended attributes was rare.  As a result, the
Mac OS X Finder was written to store the necessary information in hidden files
named ``.DS_Store``, which it places into every directory where it needs to
store information.

The format of these files is, sadly, not documented by Apple.  This is a pain
for software developers, who often distribute their software in Apple Disk
Image (or ``.dmg``) files.  Typically developers set an attractive background
on their disk images, increase the icon size and font size and often include a
link to the ``/Applications`` folder.  Unfortunately, the only supported way
to set many of these things is via Finder itself.  You might think that you
could drive Finder with AppleScript for this purpose, but this turns out to be
unreliable (Finder may not save the changes to the ``.DS_Store`` file
immediately), and worse still Apple has made changes to the information Finder
uses between versions of Mac OS X, such that setting some of these things on
newer versions of the OS X Finder will not set them for users of older
versions.

This module allows programmatic access to and construction of ``.DS_Store``
files directly from Python, with no Mac OS X specific code involved.

Usage
=====

Typical usage looks like this::

  from ds_store import DSStore

  with DSStore.open('/Users/alastair/.DS_Store', 'r+') as d:
    # Position the icon for "foo.txt" at (128, 128)
    d['foo.txt']['Iloc'] = (128, 128)

    # Display the plists for this folder
    print d['.']['bwsp']
    print d['.']['icvp']

**Importantly**, *deleting the* :class:`~ds_store.DSStore` *object is not
sufficient to flush changes to disk*.  If you use the ``with`` syntax above,
changes you make to the ``.DS_Store`` file will automatically be persisted.
Otherwise, you will need to call :meth:`~ds_store.DSStore.flush`
or :meth:`~ds_store.DSStore.close` to flush your changes to disk.

Note that Finder generally places information about folders in the
*containing* folder.  The exception is that if it cannot write to the
containing folder, or the folder in question is at the root of a volume,
Finder will put the information in a record for "." inside the folder to which
it applies.

``ds_store`` currently knows how to decode the following items

.. table:: Supported item codes

   ========  ========  ========================
   Code      Type      Python representation
   ========  ========  ========================
   ``Iloc``  ``blob``  ``(x, y)`` tuple
   ``bwsp``  ``blob``  Property list (``dict``)
   ``lsvp``  ``blob``  Property list (``dict``)
   ``lsvP``  ``blob``  Property list (``dict``)
   ``icvp``  ``blob``  Property list (``dict``)
   ========  ========  ========================

Items not in the list above will be returned as ``(type, value)`` tuples.
Supported ``type`` values are

.. table:: Suported type codes

   ========  ===============================
   Type      Python representation
   ========  ===============================
   ``bool``  Boolean (``True`` or ``False``)
   ``long``  Integer
   ``shor``  Integer
   ``ustr``  Unicode string
   ``type``  4-character byte string
   ``comp``  Integer
   ``dutc``  Integer
   ``blob``  Byte string
   ========  ===============================

If ``ds_store`` happens across any other type code, it will raise
:class:`ValueError`.  This is unavoidable because the ``.DS_Store`` file
format does not include length information, so if we find a type code we do
not support, we cannot read the file.

Code Documentation
==================

.. toctree::
   :maxdepth: 2

   ds_store


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
