# Building and running from source
While it is recommended to run Bobber using the latest Python wheel available on
the [GitHub Releases](https://github.com/NVIDIA/Bobber/releases) page, it is
possible to run Bobber directly from source, either by building and installing a
wheel locally or using Python to call specific Bobber modules.

**NOTE:** If any changes are made to the application, any Bobber containers must
be killed and re-launched to pickup the changes. This can be done with the
following which is expected to be run after building and installing a new wheel
or modifying code locally:

```
docker kill bobber  # Only necessary if Bobber is already running
bobber cast /path/to/storage  # If a new wheel was built/installed
# OR
python3 -m bobber.bobber cast /path/to/storage  # If modifying and running code directly
```

## Running the Python modules
To run the code directly using Python, first ensure all dependencies are
installed using PIP. This can be done globally using `sudo`, or in a virtual
environment with `virtualenv` or Anaconda.

```
sudo pip3 install -r requirements.txt
```

Once installed, Bobber can be called directly by calling the `bobber` package:

```
python3 -m bobber.bobber ...
```

Using `python3 -m bobber.bobber ...` is analogous to running `bobber ...` from
the installed wheel with the exception of calling the code directly. The above
command needs to be run from the root `bobber` directory of the repo.

For example, to build the Bobber image directly from the code, run the
following:

```
cd ~/bobber
python3 -m bobber.bobber build
```

## Building a Python wheel
A Python wheel can be built directly from the source and installed to replace
any existing Bobber wheels and run Bobber as normal without calling the code. A
bash script has been created which automatically builds a development version of
the Python wheel based on the local changes. Running the `./build-dev-wheel`
script will update the version number to a dev version with a timestamp and
build a new wheel of the current code with the updated version. By adding
`minor` or `patch` to the script as an argument, the minor and patch version
will be updated in addition to the timestamp, respectively.

For example, to build a dev wheel without updating the minor or patch versions,
run:

```
./build-dev-wheel
```

If the current version of the package is `6.0.0`, this will generated a new
wheel in the local `dist/` directory (which will be created if not already done)
with the version `6.0.0.dev20210211161542` depending on the time the script was
run.

Likewise, running

```
./build-dev-wheel patch
```

will generate a wheel in `dist/` with version `6.0.1.dev20210211161542` and

```
./build-dev-wheel minor
```

will generate a wheel in `dist/` with version `6.1.0.dev20210211161542`.

To generate a wheel manually without altering the version number, run

```
python3 setup.py bdist_wheel sdist
```

### Installing the built wheel
Install the generated wheel by ignoring any existing packages using PIP:

```
sudo pip3 install --ignore-installed dist/nvidia_bobber-<version>.whl
```

Bobber can now be used normally with `bobber ...` targeting the code as written
when the wheel was built.
