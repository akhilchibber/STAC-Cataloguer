# STAC Asset Information Extraction: A Comprehensive Guide

In this Github Repository, we aim to provide a clear overview of the specific STAC asset information we obtain from each data format, including (i) Vector, (ii) Raster, (iii) Non-Geospatial formats, and (iv) Indoor Mapping Data Format (IMDF). Our tool of choice is a Python function that follows the standardized STAC specifications to extract asset information. We aren't discussing the mechanics of extraction, but rather focusing on the specifics of the output: the metadata derived from these diverse data formats. This page serves as a comprehensive guide to understanding the information extracted within STAC assets across various data formats used at UNL. 

In our current scenario, we are focusing on four principal categories of data formats:

### 1. Vector Dataset
### 2. Raster Dataset
### 3. Non-Geospatial Images
### 4. Indoor Mapping Data Format (IMDF)


## 1. Vector Dataset:
<p align="center">
  <img src="https://github.com/akhilchibber/STAC-Cataloguer/blob/main/vector_data.png?raw=true" alt="earthml Logo">
</p>

The Vector datasets that we are handling include the formats  .geojson, .las, and .fgp. From these formats, we extract the following STAC asset information:

1.1. Location (href): We capture the direct link or reference to the location of the file.

1.2. Data Type: We record the data type, which is determined by the file format - 'application/geo+json' for a .geojson file and 'application/octet-stream' for .las, and .fgb files.

1.3. Dataset Type: We document the geographical characteristics of the data, which can be 'Point Cloud' for .las, 'Polygon' for .geojson and .fgp files.

1.4. Number of Features: We retrieve the total count of features in the dataset.


## 2. Raster Dataset:
<p align="center">
  <img src="https://github.com/akhilchibber/STAC-Cataloguer/blob/main/raster_data.png?raw=true" alt="earthml Logo">
</p>
For Raster datasets, we are specifically working with the Geo-Tiff datasets in the .tif format. From these, we extract the following STAC asset information:

2.1. Location (href): Similar to vector datasets, we document the direct link or reference to the file location.

2.2. Data Type: The data type for raster datasets in .tif format is 'image/tiff', which we record.

2.3. Grid Structure Details: We obtain comprehensive information regarding the pixel structure of the raster data, including (i) cell size, (ii) number of rows and columns, (iii) Coordinate reference System (CRS), and (iv) Bounding Box.

2.4. Resolution: We note down the spatial resolution of the raster data, indicating the area on the ground each pixel represents.

2.5. Pixel Statistics: We extract statistics about the pixel values, including the (i) mean, (ii) median, (iii) minimum & maximum, (iv) and standard deviation.

2.6. Band Information: For multi-band raster datasets, we extract band-related information including (i) Number of Bands, (ii) Band Names, and (iii) Band Statistics.


## 3. Non-Geospatial Images:
<p align="center">
  <img src="https://github.com/akhilchibber/STAC-Cataloguer/blob/main/jpeg_png.png?raw=true" alt="earthml Logo">
</p>

For Non-Geospatial images, we are including PNG and JPEG file formats captured by mobile cameras. Despite not being traditional geospatial datasets, from these image files we are capturing the following metadata:

3.1. Location (href): Similar to other datasets, we document the direct link or reference to the file location.

3.2. Data Type: The data type corresponds to the file format, and we record it as 'image/jpeg' for JPEG files and 'image/png' for PNG files.

3.3. Capture Time: The timestamp indicating when the image was captured is obtained and recorded, giving us context about when the data was generated.

3.4. Location Metadata (if available): If the image file includes embedded location metadata, like GPS coordinates, we extract this geospatial information. Note, however, that this data's presence depends on the device's settings that captured the image.

3.5. Camera Details: Where possible, we extract information about the capturing device. This includes (i) Camera Make & Model, and (ii) Camera Settings.

3.6. Image Details: We also extract certain image-related information, including (i) Image Dimensions, (ii) Color Space, and (iii) Compression.

 
Note: Handling Images Without Geolocation Data

In handling non-geospatial assets like JPEG and PNG files, we assign a default geohash '7zzzzzzzzz' to represent a bounding box around the point (0,0) with a precision of 10. This is a workaround that allows us to incorporate these assets into our STAC Catalog while maintaining our Item ID structure ("cellid_vpnid"). Consequently, for non-geospatial data, the STAC Item ID will take the format "7zzzzzzzzz_vpnid". This approach adheres to the STAC specifications but is subject to revisions as we explore optimal methods for handling non-geospatial data.


## 4. Indoor Mapping Data Format (IMDF) (Not Supported in Cataloguer Services yet)
<p align="center">
  <img src="https://github.com/akhilchibber/STAC-Cataloguer/blob/main/imdf.png?raw=true" alt="earthml Logo">
</p>
Indoor Mapping Data Format (IMDF) is a data model Apple introduced to represent indoor spaces. It's an open standard format which provides a generalized, yet comprehensive model for any indoor location, covering spaces like buildings and airports. For IMDF datasets, the extraction process retrieves the following STAC asset information:

4.1. Location (href): We capture the direct link or reference to the IMDF file's location.

4.2. Data Type: The data type for IMDF datasets is 'model/vnd.apple.pkage'.

4.3. Indoor Features: IMDF data is rich in terms of the range of elements it covers, these include (i) Venues, (ii) Buildings, (iii) Levels, (iv) Units, (v) Occupants, (vi) Opening Hours, and (vii) Relationships, amongst others. We extract and document these specific features from the dataset.

4.4. Feature Geometry: We capture the geometry of features, which can be in the form of Points, Polygons, or MultiPolygons, representing specific locations or areas within the indoor space.

4.5. Levels & Floor Plans: Each IMDF file often includes multiple floor levels of a building or venue. For each level, we record details like (i) Level name, (ii) Ordinal (floor number), and (iii) Height Above Ground.

4.6. Relationships: IMDF allows for complex relationships between features such as adjacency, kiosks, and accessibility. We extract this data, providing insights into the layout and dynamics of the indoor space.

4.7. Feature Count: We count the total number of features within the IMDF dataset.

 
Note: IMDF Validation

IMDF data must conform to specific Apple-defined standards. Our extraction process will run an IMDF validation and report on the compliance of the data, identifying any issues that need to be addressed.


## Conclusion:
<p align="center">
  <img src="https://github.com/akhilchibber/STAC-Cataloguer/blob/main/conclusion.jpg?raw=true" alt="earthml Logo">
</p>
This Github Repository serves as an expanded guide to the specifics of the SpatioTemporal Asset Catalog (STAC) information that our Python-based function using an API End-Point extracts from different types of data formats. This now includes Vector datasets (.geojson, .las, and .fgp), Raster datasets (Geo-Tiff in .tif format), Non-Geospatial images (JPEG and PNG), and the recently included Indoor Mapping Data Format (IMDF).<br>    

Each data format contributes a distinct set of information to the STAC Asset, ranging from standard metadata like location and data type, to more format-specific details such as grid structure for raster data, camera details for non-geospatial images, and structural details from IMDF. The inclusion of IMDF further showcases our commitment to provide a robust and diverse STAC Catalog, enhancing our understanding and usability of the data we work with. It's important to note that the support for additional formats or the extraction of more extensive information will require updating our Python function and this Github Repository accordingly.

As always, we highly value any feedback and encourage readers to leave comments about potential improvements to our cataloging mechanism. Our commitment to keeping up with technological advancements and supporting more formats in the future is driven by our ideas and needs. Please do not hesitate to contribute any possible thoughts and concerns.
