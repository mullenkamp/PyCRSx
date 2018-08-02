"""
# PyCRS

PyCRS is a pure Python GIS package for reading, writing, and converting between various
common coordinate reference system (CRS) string and data source formats.


## Introduction

Python should have a standalone GIS library focused solely on coordinate reference system metadata.
That is, a library focused on the various formats used to store and represent crs definitions, including
OGC WKT, ESRI WKT, Proj4, and various short-codes defined by organizations like EPSG, ESRI, and SR-ORG.
Correctly parsing and converting between these formats is essential in many types of GIS work.
For instance when trying to use PyProj to transform coordinates from a non-proj4 crs format. Or
when wanting to convert the crs from a GeoJSON file to a .prj file. Or when simply adding a crs definition
to a file that was previously missing one.

When I created PyCRS, the only way to read and convert between crs formats was to use the extensive Python
GDAL suite and its srs submodule, but the requirements of some applications might exclude the use of
GDAL. There have also been some online websites/services, but these only allow partial lookups or
one-way conversion from one format to another. I therefore hope that PyCRS will make it easier for
lightweight applications to read a broader range of data files and correctly interpret and possibly transform
their crs definitions. Written entirely in Python I also hope it will help clarify the differences
between the various formats, and make it easier for more people to help keep it up-to-date and bug-free.


## Status

Currently, the supported formats are OGC WKT (v1), ESRI WKT, Proj4, and any EPSG, ESRI, or SR-ORG code
available from spatialreference.org. In the future I hope to add support for OGC URN identifier strings,
and GeoTIFF file tags.

The package is still in alpha version, so it will not perfectly parse or convert between all crs,
and it is likely to have several (hopefully minor) differences from the results of other parsers like GDAL.
In the source repository there is a tester.py script, which uses a barrage of commonly
used crs as listed on http://www.remotesensing.org/geotiff/proj_list/. Currently, the overall success rate
for loading as well as converting between the three main formats is 70-90%, and visual inspections of
rendering the world with each crs generally look correct. However, whether the converted crs strings
are logically equivalent to each other from a mathematical standpoint is something that needs a more detailed
quality check.


## Platforms

Python 2 and 3, all systems (Windows, Linux, and Mac).


## Dependencies

Pure Python, no dependencies.


## Installing it

PyCRS is installed with pip from the commandline:

    pip install pycrs

It also works to just place the "pycrs" package folder in an importable location like
"PythonXX/Lib/site-packages".


## Example Usage

Begin by importing the pycrs module:

    import pycrs

### Reading

The first point of action when dealing with a data source's crs is that you should be able to
parse it correctly. In most situations this will mean reading the ESRI .prj file that accomponies
a shapefile or some other file. PyCRS has a convenience function for doing that:

    fromcrs = pycrs.loader.from_file("path/to/shapefilename.prj")

The same function also supports reading the crs from GeoJSON files:

    fromcrs = pycrs.loader.from_file("path/to/geojsonfile.json")

If your crs is not defined in a file there are also functions for that. For instance if you know the url
where the crs is defined you can do:

    fromcrs = pycrs.loader.from_url("www.somesite.com/someproj")

Or if you are provided with the actual string representation of the crs, given by a web service for
instance, you can load it using the appropriate function from the parser module or let PyCRS autodetect
and load the crs type for you:

    fromcrs = pycrs.parser.from_unknown_text(somecrs_string)

### Converting

Once you have read the crs of the original data source, you may want to convert it to some other crs format.
A common reason for wanting this for instance, is if you want to reproject the coordinates of your spatial
data. In Python this is typically done with the PyProj module which only takes proj4 strings, so you would
have to convert your datasource's crs to proj4:

    fromcrs_proj4 = fromcrs.to_proj4()

You can then use PyCRS to define your target projection in the string format of your choice, before converting
it to the proj4 format that PyProj expects:

    tocrs = pycrs.parser.from_esri_code(54030) # Robinson projection from esri code
    tocrs_proj4 = tocrs.to_proj4()

With the source and target projections defined in the proj4 crs format, you are ready to transform your
data coordinates with PyProj, which is not covered here.

### Writing

After you transform your data coordinates you may also wish to save the data back to file along with the new
crs. With PyCRS you can do this in a variety of crs format. For instance:

    with open("shapefile.prj", "w") as writer:
        writer.write(tocrs.to_esri_wkt())

PyCRS also gives access to each crs element and parameter that make up a crs in the "elements" subpackage,
so you could potentially also build a crs from scratch and then save it to a format of your choice.
Inspect the parser submodule source code for inspiration on how to go about this.


## More Information:

This tutorial only covered some basic examples. For the full list of functions and supported crs formats,
check out the API Documentation.

- [Home Page](http://github.com/karimbahgat/PyCRS)
- [API Documentation](http://pythonhosted.org/PyCRS)


## License:

This code is free to share, use, reuse,
and modify according to the MIT license, see license.txt


## Credits:

- Karim Bahgat
- Micah Cochrain
- Wassname

"""

__version__ = "1.0.2"


from . import loader
from . import parser
from . import utils




