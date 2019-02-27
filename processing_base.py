import json
import rasterio
import numpy as np
import rasterio.features
from skimage import io
import matplotlib.pyplot as plt
from skimage import morphology
import png


box = []
shape_array = []
lista = io.imread('Amazonas2017.tif')

with rasterio.open('Amazonas2017.tif') as src:
    box = src.transform

lista[np.where(lista < 0.9)] = 0
lista[np.where(lista >= 0.9)] = 1



first = morphology.remove_small_objects(lista.astype(bool), min_size=800, connectivity=4)
first_int = first.astype(np.int16)

# plt.imshow(lista)
# plt.imshow(golay)
# plt.show()

for shape, value in rasterio.features.shapes(first_int, transform=box, connectivity=8):
    if value == 1:
        shape_array.append(shape)

data = {"type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}}
feature_array = []
feature_ex = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}}

for shape in shape_array:
    feature_ex['geometry']['coordinates'] = shape['coordinates']
    feature_array.append(feature_ex)
    feature_ex = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}}

data['features'] = feature_array

with open('riverAmazonas2017.geojson', 'w') as fout:
    json.dump(data, fout)



