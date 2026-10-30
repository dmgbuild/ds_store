# Release History

<!-- towncrier release notes start -->

## 1.3.3 (2026-06-23)

### Features

* Values stored as binary property lists (e.g., `lsvC`) are now decoded when displayed by the `ds_store` command line tool. ([#219](https://github.com/dmgbuild/ds_store/issues/219))

### Bugfixes

* The `ds_store` command line tool once again produces output, and debug output from `DSStore._dump_node()` and `DSStore._dump_super()` was restored. ([#217](https://github.com/dmgbuild/ds_store/issues/217))

### Misc

* [#211](https://github.com/dmgbuild/ds_store/issues/211), [#212](https://github.com/dmgbuild/ds_store/issues/212), [#213](https://github.com/dmgbuild/ds_store/issues/213), [#214](https://github.com/dmgbuild/ds_store/issues/214), [#215](https://github.com/dmgbuild/ds_store/issues/215), [#216](https://github.com/dmgbuild/ds_store/issues/216), [#221](https://github.com/dmgbuild/ds_store/issues/221)

## 1.3.2 (2025-12-04)

### Features

* Support for Python 3.13, 3.14 and 3.15 was added. ([#17](https://github.com/dmgbuild/ds_store/issues/17), [#196](https://github.com/dmgbuild/ds_store/issues/196))

### Bugfixes

* The minimum required version of `mac_alias` was increased to 2.2.2, for compatibility with Apple Silicon. ([#78](https://github.com/dmgbuild/ds_store/issues/78))

### Backward Incompatible Changes

* Support for Python 3.7, 3.8 and 3.9 was dropped. ([#103](https://github.com/dmgbuild/ds_store/issues/103), [#196](https://github.com/dmgbuild/ds_store/issues/196))

### Misc

* [#24](https://github.com/dmgbuild/ds_store/issues/24), [#59](https://github.com/dmgbuild/ds_store/issues/59), [#77](https://github.com/dmgbuild/ds_store/issues/77), [#79](https://github.com/dmgbuild/ds_store/issues/79), [#151](https://github.com/dmgbuild/ds_store/issues/151), [#192](https://github.com/dmgbuild/ds_store/issues/192), [#193](https://github.com/dmgbuild/ds_store/issues/193)

## 1.3.1 (2022-11-24)

### Features

* The `ds_store` command line tool is now installed as a console script entry point, and can be invoked as `python -m ds_store`.
* Support for Python 3.10, 3.11 and 3.12 was added.

### Bugfixes

* A typo that caused a failure when splitting nodes while inserting entries was corrected. ([#8](https://github.com/dmgbuild/ds_store/issues/8))

### Backward Incompatible Changes

* Support for Python 2, and Python 3 versions prior to 3.7 was dropped.

### Misc

* [#9](https://github.com/dmgbuild/ds_store/issues/9), [#10](https://github.com/dmgbuild/ds_store/issues/10), [#11](https://github.com/dmgbuild/ds_store/issues/11), [#12](https://github.com/dmgbuild/ds_store/issues/12), [#13](https://github.com/dmgbuild/ds_store/issues/13), [#16](https://github.com/dmgbuild/ds_store/issues/16)

## 1.3.0 (2020-10-15)

### Bugfixes

* `plistlib` is now used in preference to `biplist` on Python 3.4+, correcting a compatibility problem with Python 3.9.

## 1.2.0 (2020-10-11)

### Features

* A `ds_store` command line tool was added, for displaying the contents of `.DS_Store` files. ([#5](https://github.com/dmgbuild/ds_store/issues/5))

### Bugfixes

* The `code` argument to `find()` is now optional, as documented. ([#3](https://github.com/dmgbuild/ds_store/issues/3))

## 1.1.2 (2017-07-27)

### Bugfixes

* A number of Python 3 compatibility problems were corrected.

## 1.1.1 (2017-07-27)

### Bugfixes

* A number of Python 3 compatibility problems were corrected.
* The previously undeclared `mac_alias` dependency was added.

## 1.1.0 (2016-12-05)

### Features

* `pBBk` entries are now decoded as `mac_alias` Bookmarks.

### Bugfixes

* A typo that prevented adding leaf nodes was corrected.
* Opening `.DS_Store` files no longer fails when data is provided as a `bytearray`.
* The `six` dependency was removed.
* A number of Python 3 compatibility problems were corrected.

## 1.0.0 (2014-02-13)

* Initial release.
