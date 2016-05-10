[Logo](doc/logo.png)

[![License](https://poser.pugx.org/automattic/jetpack/license.svg)](http://www.gnu.org/licenses/gpl-2.0.html)

This repository contains all of OpenBikes's backend code. It is split in the following way:

- [`collecting`](collecting/) for fetching biking and weather data.
- [`mongo`](mongo/) for storing data split into 3 collections.
	- [`timeseries`](mongo/timeseries/) for the biking data.
	- [`weather`](mongo/weather/) for the weather data.
- [`training`](training/) for machine learning.
- [`app`](app/) for exposing an API and providing an administration interface.

Consult the [wiki](https://github.com/OpenBikes/Website/wiki) for detailed documentation on this repository. Refer to the [API documentation](docs.openbikes.apiary.io) if you want to build an application by consuming the OpenBikes API.
