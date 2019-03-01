# -*- encoding: utf-8 -*-
from shapely.geometry import mapping, shape
import fiona
import argparse
from centerline import Centerline


class Shp2centerline(object):

    def __init__(self, inputSHP, outputSHP, dist):
        self.inshp = inputSHP
        self.outshp = outputSHP
        self.dist = abs(dist)
        self.dct_polygons = {}
        self.dct_polygons_temp = {}
        self.dct_centerlines = {}
        self.id_counter = 0

        print ('Importing polygons from: ' + self.inshp)
        self.importSHP()
        print ('Calculating centerlines.')
        self.run()
        print ('Exporting centerlines to: ' + self.outshp)
        self.export2SHP()
        print ('Calculation complete.')


    def run(self):
        """
        Starts processing of the imported SHP file.

        """

        # for k in self.dct_polygons.keys():
        #     poly_geom = self.dct_polygons[k]
        #     print(len(poly_geom.exterior.coords.xy[0]))
        #     centerlineObj = Centerline(poly_geom,self.dist)
        #     self.dct_centerlines[k] = centerlineObj.createCenterline()

        r = dict(self.dct_polygons)
        # print("BEFORE")
        # print(self.dct_polygons)

        for i in r.keys():
            poly_geom = r[i]
            print("LEN")
            print(len(poly_geom.exterior.coords.xy[0]))
            # if len(poly_geom.exterior.coords.xy[0]) < 12 or i == 16:
            if len(poly_geom.exterior.coords.xy[0]) < 500:
                del self.dct_polygons[i]

        for k in self.dct_polygons.keys():
            poly_geom = self.dct_polygons[k]
            # print("ONLY ONES")
            # print(len(poly_geom.exterior.coords.xy[0]))
            # print("YO")
            # print(poly_geom)
            centerlineObj = Centerline(poly_geom, self.dist)
            self.dct_centerlines[k] = centerlineObj.createCenterline()
            # print("CENTERLINES")
            # print(k)
            # print(self.dct_centerlines[k])





    def importSHP(self):
        """
        Imports the Shapefile into a dictionary. Shapefile has to have ID
        column with unique values.

        Returns:
            a dictionary where the ID is the key, and the value is a polygon
            geometry.
        """

        with fiona.open(self.inshp, 'r', encoding = 'UTF-8') as fileIN:
            for polygon in fileIN:
                # print("POLYGON FEATURES")
                # print(len(polygon["features"]))
                # print(polygon)
                # print(len(polygon["geometry"]["coordinates"][0]))
                # polygonID = polygon['properties'][u'id']
                polygonID = self.id_counter
                geom = shape(polygon['geometry'])
                print("GEOM")
                print(geom)
                self.id_counter = self.id_counter + 1


                self.dct_polygons[polygonID] = geom


    def export2SHP(self):
        """
        Creates a Shapefile and fills it with centerlines and their IDs.

        The dictionary contains the IDs of the centerlines (keys) and their
        geometries (values). The ID of a centerline is the same as the ID of
        the polygon it represents.
        """

        newschema = {'geometry': 'MultiLineString',
                    'id': 'int',
                    'properties': {'id': 'int'}}

        with fiona.open(self.outshp, 'w', encoding='UTF-8', \
            schema = newschema, driver = 'ESRI Shapefile') as SHPfile:

            for i, key in enumerate(self.dct_centerlines):
                geom = self.dct_centerlines[key]
                newline = {}

                newline['id'] = key
                newline['geometry'] = mapping(geom)
                newline['properties'] = {'id': key}

                print("NEWLINE")
                print(newline)

                if newline["geometry"]["type"] != "GeometryCollection":
                    SHPfile.write(newline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Calculate the centerline of a polygon')

    parser.add_argument('SRC', type = str, help = 'Name of the input Shapefile')
    parser.add_argument('DEST', type = str, help = 'Name of the output Shapefile')
    parser.add_argument('DINTER', type = float, nargs = '?', default = 0.5,
                        help = 'Factor of interpolation (by default: 0.5)')
    args = parser.parse_args()

    Shp2centerline(args.SRC, args.DEST, args.DINTER)
