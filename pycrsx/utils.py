"""
Misc utility functions related to crs formats and online services.
"""

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import re
from pycrsx import parser

#########################################
### Dictionaries for convert_crs

proj4_netcdf_var = {'x_0': 'false_easting', 'y_0': 'false_northing', 'f': 'inverse_flattening',
                    'lat_0': 'latitude_of_projection_origin',
                    'lon_0': ('longitude_of_central_meridian', 'longitude_of_projection_origin'),
                    'pm': 'longitude_of_prime_meridian',
                    'k_0': ('scale_factor_at_central_meridian', 'scale_factor_at_projection_origin'),
                    'a': 'semi_major_axis', 'b': 'semi_minor_axis', 'lat_1': 'standard_parallel',
                    'proj': 'transform_name'}

proj4_netcdf_name = {'aea': 'albers_conical_equal_area', 'tmerc': 'transverse_mercator',
                     'aeqd': 'azimuthal_equidistant', 'laea': 'lambert_azimuthal_equal_area',
                     'lcc': 'lambert_conformal_conic', 'cea': 'lambert_cylindrical_equal_area',
                     'longlat': 'latitude_longitude', 'merc': 'mercator', 'ortho': 'orthographic',
                     'ups': 'polar_stereographic', 'stere': 'stereographic', 'geos': 'vertical_perspective'}

###########################################
### Functions

def build_crs_table(savepath):
    """
    Build crs table of all equivalent format variations by scraping spatialreference.org.
    Saves table as tab-delimited text file.
    NOTE: Might take a while.

    Arguments:

    - *savepath*: The absolute or relative filepath to which to save the crs table, including the ".txt" extension.
    """
    # create table
    outfile = open(savepath, "wb")

    # create fields
    fields = ["codetype", "code", "proj4", "ogcwkt", "esriwkt"]
    outfile.write("\t".join(fields) + "\n")

    # make table from url requests
    for codetype in ("epsg", "esri", "sr-org"):
        print(codetype)

        # collect existing proj list
        print("fetching list of available codes")
        codelist = []
        page = 1
        while True:
            try:
                link = 'http://spatialreference.org/ref/%s/?page=%s' %(codetype,page)
                html = urllib2.urlopen(link).read()
                codes = [match.groups()[0] for match in re.finditer(r'/ref/'+codetype+'/(\d+)', html) ]
                if not codes: break
                print("page",page)
                codelist.extend(codes)
                page += 1
            except:
                break

        print("fetching string formats for each projection")
        for i,code in enumerate(codelist):

            # check if code exists
            link = 'http://spatialreference.org/ref/%s/%s/' %(codetype,code)
            urllib2.urlopen(link)

            # collect each projection format in a table row
            row = [codetype, code]
            for resulttype in ("proj4", "ogcwkt", "esriwkt"):
                try:
                    link = 'http://spatialreference.org/ref/%s/%s/%s/' %(codetype,code,resulttype)
                    result = urllib2.urlopen(link).read()
                    row.append(result)
                except:
                    pass

            print("projection %i of %i added" %(i,len(codelist)) )
            outfile.write("\t".join(row) + "\n")

    # close the file
    outfile.close()


def crscode_to_string(codetype, code, format):
    """
    Lookup crscode on spatialreference.org and return in specified format.

    Arguments:

    - *codetype*: "epsg", "esri", or "sr-org".
    - *code*: The code.
    - *format*: The crs format of the returned string. One of "ogcwkt", "esriwkt", or "proj4", but also several others...

    Returns:

    - Crs string in the specified format.
    """
    link = 'http://spatialreference.org/ref/%s/%s/%s/' %(codetype,code,format)
    result = urllib2.urlopen(link).read()
    if not isinstance(result, str):
        result = result.decode()
    return result

##def crsstring_to_string(string, newformat):
##    """
##    Search unknown crs string for a match on spatialreference.org.
##    Not very reliable, the search engine does not properly lookup all text.
##    If string is correct there should only be one correct match.
##    Warning: Not finished yet.
##    """
##    link = 'http://spatialreference.org/ref/?search=%s' %string
##    searchresults = urllib2.urlopen(link).read()
##    # pick the first result
##    # ...regex...
##    # go to its url, with extension for the newformat
##    link = 'http://spatialreference.org/ref/%s/%s/%s/' %(codetype,code,newformat)
##    result = urllib2.urlopen(link).read()
##    return result


def convert_crs(from_crs, crs_type='proj4', pass_str=False):
    """
    Convenience function to convert one crs format to another.

    Parameters
    ----------
    from_crs: int or str
        The crs as either an epsg number or a str in a common crs format (e.g. proj4 or wkt).
    crs_type: str
        Output format type of the crs ('proj4', 'wkt', 'proj4_dict', or 'netcdf_dict').
    pass_str: str
        If input is a str, should it be passed though without conversion?

    Returns
    -------
    str or dict
    """

    ### Load in crs
    if all([pass_str, isinstance(from_crs, str)]):
        crs2 = from_crs
    else:
        if isinstance(from_crs, int):
            crs1 = parser.from_epsg_code(from_crs)
        elif isinstance(from_crs, str):
            crs1 = parser.from_unknown_text(from_crs)
        else:
            raise  ValueError('from_crs must be an int or str')

        ### Convert to standard formats
        if crs_type == 'proj4':
            crs2 = crs1.to_proj4()
        elif crs_type == 'wkt':
            crs2 = crs1.to_ogc_wkt()
        elif crs_type in ['proj4_dict', 'netcdf_dict']:
            crs1a = crs1.to_proj4()
            crs1b = crs1a.replace('+', '').split()[:-1]
            crs1c = dict(i.split('=') for i in crs1b)
            crs2 = dict((i, float(crs1c[i])) for i in crs1c)
        else:
            raise ValueError('Select one of "proj4", "wkt", "proj4_dict", or "netcdf_dict"')
        if crs_type == 'netcdf_dict':
            crs3 = {}
            for i in crs2:
                if i in proj4_netcdf_var.keys():
                    t1 = proj4_netcdf_var[i]
                    if isinstance(t1, tuple):
                        crs3.update({j: crs2[i] for j in t1})
                    else:
                        crs3.update({proj4_netcdf_var[i]: crs2[i]})
            if crs3['transform_name'] in proj4_netcdf_name.keys():
                gmn = proj4_netcdf_name[crs3['transform_name']]
                crs3.update({'transform_name': gmn})
            else:
                raise ValueError('No appropriate netcdf projection.')
            crs2 = crs3

    return crs2


