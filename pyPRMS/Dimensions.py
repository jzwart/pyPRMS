
from __future__ import (absolute_import, division, print_function)
from future.utils import iteritems

from collections import OrderedDict

from pyPRMS.constants import DIMENSION_NAMES
from pyPRMS.prms_helpers import read_xml


def _valid_dimension_name(name):
    """Returns true if given dimension name is a valid name for PRMS"""
    return name in DIMENSION_NAMES


class Dimension(object):
    """Defines a single dimension"""
    # Container for a single dimension
    def __init__(self, name=None, size=0):
        self.__name = None
        self.__size = None
        self.name = name  # Name of the dimension
        self.size = size  # integer

    @property
    def name(self):
        """Return the name of the dimension"""
        return self.__name

    @name.setter
    def name(self, name):
        if _valid_dimension_name(name):
            self.__name = name
        else:
            # TODO: Should this raise an error?
            raise ValueError('Dimension name, {}, is not a valid PRMS dimension name'.format(name))

    @property
    def size(self):
        """"Return the size of the dimension"""
        return self.__size

    @size.setter
    def size(self, value):
        """Set the size of the dimension"""
        if not isinstance(value, int) or value < 0:
            raise ValueError('Dimension size must be a positive integer')
        self.__size = value

    def __repr__(self):
        return 'Dimension(name={}, size={!r})'.format(self.name, self.size)

    def __iadd__(self, other):
        # augment in-place addition so the instance plus a number results
        # in a change to self.__size
        if not isinstance(other, int):
            raise ValueError('Dimension size type must be an integer')
        self.__size += other
        return self

    def __isub__(self, other):
        # augment in-place addition so the instance minus a number results
        # in a change to self.__size
        if not isinstance(other, int):
            raise ValueError('Dimension size type must be an integer')
        if self.__size - other < 0:
            raise ValueError('Dimension size must be positive')
        self.__size -= other
        return self


class Dimensions(object):
    """Container of Dimension objects"""
    # Container for a collection of dimensions
    def __init__(self):
        self.__dimensions = OrderedDict()  # ordered dictionary of Dimension()

    def __str__(self):
        outstr = ''
        if len(self.__dimensions) == 0:
            outstr = '<empty>'
        else:
            for kk, vv in iteritems(self.__dimensions):
                outstr += '{}: {}\n'.format(kk, vv)
        return outstr

    def __getattr__(self, name):
        return getattr(self.__dimensions, name)

    def __getitem__(self, item):
        """Get named dimension"""
        return self.__dimensions[item]

    @property
    def dimensions(self):
        """Returns ordered dictionary of Dimension objects"""
        # Return the ordered dictionary of defined dimensions
        return self.__dimensions

    @property
    def ndims(self):
        # Number of dimensions
        return len(self.__dimensions)

    def add(self, name, size=0):
        # This method adds a dimension if it doesn't exist
        # TODO: check for valid dimension size for ndays, nmonths, and one
        if name not in self.__dimensions:
            try:
                self.__dimensions[name] = Dimension(name=name, size=size)
            except ValueError as err:
                print(err)
        else:
            # TODO: Should this raise an error?
            print('Dimension {} already exists...skipping add name'.format(name))

    def add_from_xml(self, filename):
        # Add dimensions and grow dimension sizes from xml information for a parameter
        # This information is found in xml files for each region for each parameter
        # No attempt is made to verify whether each region for a given parameter
        # has the same or same number of dimensions.
        xml_root = read_xml(filename)

        for cdim in xml_root.findall('./dimensions/dimension'):
            name = cdim.get('name')
            size = int(cdim.get('size'))
            pos = int(cdim.get('position')) - 1

            if name not in self.__dimensions:
                try:
                    self.__dimensions[name] = Dimension(name=name, size=size)
                except ValueError as err:
                    print(err)
            else:
                if self.__dimensions.keys().index(name) != pos:
                    # This indicates a problem in one of the paramdb files
                    raise ValueError('{}: Attempted position change from {} to {}'.format(name,
                                                                                          self.__dimensions[name].position,
                                                                                          pos))
                else:
                    if name not in ['nmonths', 'ndays', 'one']:
                        # NOTE: This will always try to grow a dimension if it already exists!
                        self.__dimensions[name].size += size

    def exists(self, name):
        """Verifies if a dimension exists"""
        return name in self.dimensions.keys()

    def get(self, name):
        """Returns the given dimensions if it exists"""
        if self.exists(name):
            return self.__dimensions[name]
        raise ValueError('Dimension, {}, does not exist.'.format(name))

    def remove(self, name):
        if self.exists(name):
            del self.__dimensions[name]

    def tostructure(self):
        """Returns a data structure of Dimensions data for serialization"""
        # Return the dimensions info/data as a data structure
        dims = {}
        for kk, vv in iteritems(self.dimensions):
            dims[kk] = {'size': vv.size}
        return dims
