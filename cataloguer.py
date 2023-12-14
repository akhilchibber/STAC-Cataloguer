'''
STAC-API CRUD Operations and Meta-Data Management:

This Python Script enables CRUD operations on STAC items and collections, including creating, reading, updating, and
deleting functionalities for both. It also includes functions for creating and deleting a STAC asset and its type.
Operations are performed using the Fast STAC-API in a PostGreSQL database.
'''


# IMPORTING ALL THE ESSENTIAL LIBRARIES
from pystac import Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent
from datetime import datetime
from datetime import timezone
import os
import fiona
import requests
import json
from geounl.GeoUtils import Quantization
from shapely.geometry import Polygon, mapping
import laspy
from geounl.GeoUtils import geodata_to_geohash
import rasterio
from PIL import Image
import PIL.ExifTags
import hashlib





# SETTING UP THE FAST STAC-API BASE URL
# base_url = "http://34.93.218.142:8080"
#base_url = "http://34.141.193.222:8080"





if 'CATALOG_SERVICE' not in os.environ:
    raise EnvironmentError(
        "Please set the environment variable CATALOG_SERVICE")
base_url = os.environ.get('CATALOG_SERVICE')





# # SETTING UP ENVIRONMENT VARIABLES FOR "SERVER" AND "PORT" AS PART OF THE "PYUNL" PYTHON LIBRARY
# os.environ['QUANTIZATION_SERVER'] = 'your_custom_server_address'
# os.environ['QUANTIZATION_PORT'] = 'your_custom_port_number'





# FUNCTION 1: GET THE METADATA OF AN IMAGE
def get_image_metadata(file_path):
    image = Image.open(file_path)

    metadata = get_basic_image_metadata(image, file_path)
    exif_data = get_exif_data(image)

    if exif_data is not None:
        metadata.update(exif_data)

    return metadata


# FUNCTION 2: GET THE BASIC METADATA OF AN IMAGE
def get_basic_image_metadata(image, file_path):
    # Get the image dimensions
    width, height = image.size

    # Get the color space and compression type
    color_space = image.mode
    compression = image.info.get('compression', None)

    return {
        'dimensions': (width, height),
        'color_space': color_space,
        'compression': compression,
    }


# FUNCTION 3: GET THE EXIF DATA OF AN IMAGE
def get_exif_data(image):

    exif_data = {}

    if hasattr(image, '_getexif'):
        raw_exif_data = image._getexif()

        if raw_exif_data is not None:
            for tag_id, value in raw_exif_data.items():
                tag_name = get_exif_tag(tag_id)

                if tag_name == 'DateTimeOriginal':
                    exif_data['capture_time'] = value
                elif tag_name == 'Make':
                    exif_data['camera_make'] = value
                elif tag_name == 'Model':
                    exif_data['camera_model'] = value

    return exif_data if exif_data else None


# FUNCTION 4: GET THE EXIF TAG FOR A GIVEN ID
def get_exif_tag(tag_id):
    exif_tags = PIL.ExifTags.TAGS
    return exif_tags.get(tag_id, tag_id)


# FUNCTION 5: THIS IS A FUNCTION FOR EXTRACTING THE "BBOX" AND GEOMETRY "COORDINATES" USING QUANTIZATION
def get_geo_info(cell_id):
    # Initialize the Quantization Class with Server and Port information
    quantization_instance = Quantization(
        server=os.environ.get('QUANTIZATION_SERVER',
                              'core-sandbox-wwpvuze6ra-ez.a.run.app'),
        port=os.environ.get('QUANTIZATION_PORT', '443')
    )

    # Get the Bounding Box and Geometry Coordinates using the Quantization instance
    geo_bounding_box = quantization_instance.bounds(cell_id)
    left, bottom = geo_bounding_box.bottom_left.lon, geo_bounding_box.bottom_left.lat
    right, top = geo_bounding_box.top_right.lon, geo_bounding_box.top_right.lat
    bbox = [left, bottom, right, top]

    # Create a Polygon geometry object representing the footprint
    footprint = Polygon([
        [left, bottom],
        [left, top],
        [right, top],
        [right, bottom]
    ])
    geometry = mapping(footprint)

    return bbox, geometry


# FUNCTION 6: THIS IS A FUNCTION TO CALCULATE THE NUMBER OF POINT FEATURES IN A .LAS FILE
def count_points_in_las(las_file_path):
    las_data = laspy.read(las_file_path)
    num_points = las_data.header.point_count
    return num_points


# FUNCTION 7: THIS IS A FUNCTION TO CALCULATE THE NUMBER OF FEATURES AND GEOMETRY TYPE IN A .GEOJSON OR .SHP FILE
def count_features_and_geometry_type(file_path):
    with fiona.open(file_path, 'r') as src:
        no_of_features = len(src)  # get the number of features
        geometry_type = src.schema['geometry']  # get the geometry type
    return no_of_features, geometry_type


# FUNCTION 8: This function opens a .tif file and returns the opened file.
def open_tif(file_path):
    dataset = rasterio.open(file_path)
    return dataset


# FUNCTION 9: THIS FUNCTION EXTRACTS THE NUMBER OF BANDS, DIMENSIONS, SPATIAL RESOLUTION FROM .tif FILE
def extract_tif_info(dataset):
    num_bands = dataset.count
    dimensions = dataset.shape
    # spatial_resolution = dataset.res
    spatial_resolution = dataset.transform[0]
    return num_bands, dimensions, spatial_resolution


# FUNCTION 10: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .tif FORMAT
def handle_tif(file_path):
    dataset = open_tif(file_path)
    num_bands, dimensions, spatial_resolution = extract_tif_info(dataset)
    geometry_type = "Raster"
    return {
        'media_type': "image/tif",
        'num_bands': num_bands,
        'dimensions': dimensions,
        'spatial_resolution': spatial_resolution,
        'geometry_type': geometry_type
    }


# FUNCTION 11: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .geojson  FORMAT
def handle_geojson(file_path):
    no_of_features, geometry_type = count_features_and_geometry_type(file_path)
    return {
        'media_type': MediaType.GEOJSON,
        'no_of_features': no_of_features,
        'geometry_type': geometry_type
    }


# FUNCTION 12: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .las FORMAT
def handle_las(file_path):
    no_of_features = count_points_in_las(file_path)
    return {
        'media_type': "application/octet-stream",
        'no_of_features': no_of_features,
        'geometry_type': "Point Cloud"
    }


# FUNCTION 13: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .csv FORMAT
def handle_csv(file_path):
    return {
        'media_type': "text/csv"
    }


# FUNCTION 14: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .shp FORMAT
def handle_shp(file_path):
    no_of_features, geometry_type = count_features_and_geometry_type(file_path)
    return {
        'media_type': "application/octet-stream",
        'no_of_features': no_of_features,
        'geometry_type': geometry_type
    }


# FUNCTION 15: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .jpg FORMAT
def handle_jpg(file_path):
    metadata = get_image_metadata(file_path)

    # Convert the data type to the format your script uses
    metadata['media_type'] = 'image/jpeg'

    return metadata


# FUNCTION 16: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .png FORMAT
def handle_png(file_path):
    metadata = get_image_metadata(file_path)

    # Convert the data type to the format your script uses
    metadata['media_type'] = 'image/png'

    return metadata


# FUNCTION 17: THIS FUNCTION CALCULATES THE REQUIRED PARAMETERS SPECIFICALLY FOR .fgb FORMAT
def handle_fgb(file_path):
    no_of_features, geometry_type = count_features_and_geometry_type(file_path)
    return {
        'media_type': "application/octet-stream",
        'no_of_features': no_of_features,
        'geometry_type': geometry_type
            }


# FUNCTION 18: THIS FUNCTION HANDLES THE REQUIRED DATASET BASED ON THE GIVEN INPUT DATASET
def select_handler(file_extension):
    if file_extension == '.geojson':
        return handle_geojson
    elif file_extension == '.las':
        return handle_las
    elif file_extension == '.csv':
        return handle_csv
    elif file_extension == '.shp':
        return handle_shp
    elif file_extension == '.tif':
        return handle_tif
    if file_extension == '.jpg' or file_extension == '.jpeg':
        return handle_jpg
    elif file_extension == '.png':
        return handle_png
    elif file_extension == '.fgb':
        return handle_fgb
    else:
        raise ValueError(f"Unsupported file type for file extension: {file_extension}")


# FUNCTION 19: THIS FUNCTION COMPUTES THE SHA256 WHICH IS USED AS AN ASSET ID
def compute_sha256_hash(input_str):
    """Compute the SHA-256 hash of the given input string."""
    return hashlib.sha256(input_str.encode()).hexdigest()


# FUNCTION 20: THIS FUNCTION GENERATES THE ASSET ID BASED ON SHA256 BY INSPECTING THE PATH AND META DATA OF THE INPUT FILE
def generate_asset_id(file_path, metadata_dict):
    """Generate a SHA-256 based Asset ID using file path and metadata."""
    # Convert the dictionary values into a string with underscore separators
    metadata_str = "_".join(str(value) for value in metadata_dict.values())

    # Concatenate with the file path
    combined_str = f"{metadata_str}_{file_path}"

    # Return the computed SHA-256 hash
    return compute_sha256_hash(combined_str)


# FUNCTION 21: THIS IS A FUNCTION TO CREATE STAC ASSET TO BE ADDED WITHIN A STAC ITEM
def create_asset_from_path(file_path, original_path):
    file_extension = os.path.splitext(file_path)[1]

    handler = select_handler(file_extension)
    fields = handler(file_path)

    asset = Asset(href=original_path,
                  media_type=fields.get('media_type') if isinstance(fields.get('media_type'),
                                                                    MediaType) else fields.get('media_type'),
                  extra_fields={})

    asset.extra_fields.update({k: v for k, v in fields.items() if v is not None})

    return asset


# FUNCTION 22: THIS IS A FUNCTION TO DELETE A LIST OF ASSETS AVAILABLE WITHIN STAC ITEM
def delete_asset_from_path(vpm_id, cell_id, assets_to_delete):
    cell_id_2 = f"{cell_id}_{vpm_id}"
    # Step 1: Get the STAC Item
    response = requests.get(
        f"{base_url}/collections/{vpm_id}/items/{cell_id_2}")
    if response.status_code == 200:
        item_data = response.json()
        # print(f"Successfully retrieved STAC Item with id {cell_id_2}")
    else:
        print(
            f"Failed to retrieve STAC Item. Response status code: {response.status_code}")
        return False

    assets_deleted = False
    # Step 2: Delete the specified assets if they exist
    for asset_to_delete in assets_to_delete:
        if asset_to_delete in item_data["assets"]:
            del item_data["assets"][asset_to_delete]
            print(f"Asset '{asset_to_delete}' has been deleted locally.")
            assets_deleted = True

    if assets_deleted:
        # If this was the last asset, delete the item
        if len(item_data["assets"]) == 0:
            delete_stac_item(vpm_id, cell_id)
            return True

        # Update the STAC Item in the database if it still contains assets
        else:
            headers = {"Content-Type": "application/json"}
            response = requests.put(f"{base_url}/collections/{vpm_id}/items/{cell_id_2}",
                                    data=json.dumps(item_data),
                                    headers=headers)
            if response.status_code == 200:
                print(f"Successfully updated STAC Item with id {cell_id_2}")
                return True
            else:
                print(
                    f"Failed to update STAC Item. Response status code: {response.status_code}")
                return False
    else:
        print("None of the assets exist in the item's assets.")
        return False


# FUNCTION 23: THIS IS A FUNCTION TO PREPARE A STAC COLLECTION
def create_stac_collection(vpm_id, licence, start_datetime=None, end_datetime=None, spatial_extent=None):

    temporal_extent = TemporalExtent(
        [[start_datetime, end_datetime]]) if start_datetime else TemporalExtent([[None, None]])
    spatial_extent = SpatialExtent(
        [spatial_extent]) if spatial_extent else SpatialExtent([[None, None, None, None]])
    extent = Extent(spatial_extent, temporal_extent)

    collection = Collection(id=vpm_id,
                            description="",
                            extent=extent,
                            license=licence)

    collection.normalize_hrefs(base_url)

    # Convert the PySTAC Collection to a dictionary, then to a JSON string
    collection_data = json.dumps(collection.to_dict())

    # # Save the Collection as a JSON file locally
    # with open(f"{vpm_id}_collection.json", 'w') as f:
    #     json.dump(collection.to_dict(), f, indent=4)

    # Send a POST request to your server to create the collection
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{base_url}/collections", data=collection_data, headers=headers)

    if response.status_code == 200:
        print(f"Successfully created STAC Collection with id {vpm_id}")
    else:
        print(
            f"Failed to create STAC Collection. Response status code: {response.status_code}")


# FUNCTION 24: THIS IS A FUNCTION TO PREPARE A STAC ITEM
def create_stac_item(vpm_id, cell_id, asset_paths, collection, original_path):
    # Define constraints for the STAC items
    item_id = f"{cell_id}_{vpm_id}"  # STAC item ID

    # Get bbox and geometry
    bbox, geometry = get_geo_info(cell_id)

    # Step 5: Define the STAC item properties
    current_datetime = datetime.now(timezone.utc)
    current_datetime_str = current_datetime.isoformat()
    parsed_datetime = datetime.fromisoformat(
        current_datetime_str.replace("Z", "+00:00"))

    item = Item(id=item_id,
                geometry=geometry,
                bbox=bbox,
                datetime=parsed_datetime,
                properties={})

    for asset_path, orig_path in zip(asset_paths, original_path):
        file_extension = os.path.splitext(asset_path)[1]
        handler = select_handler(file_extension)
        fields = handler(asset_path)

        asset_id = generate_asset_id(asset_path, fields)
        asset = create_asset_from_path(asset_path, orig_path)
        item.add_asset(asset_id, asset)

    # Convert the PySTAC Item to a dictionary, then to a JSON string
    item_data = json.dumps(item.to_dict())

    # Send a POST request to your server to create the item
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{base_url}/collections/{vpm_id}/items",
                             data=item_data,
                             headers=headers)

    if response.status_code == 200:
        print(f"Successfully created STAC Item with id {item_id}")
    else:
        print(
            f"Failed to create STAC Item. Response status code: {response.json()}")

    return item


# FUNCTION 25: THIS IS A FUNCTION TO READ A STAC COLLECTION
def read_stac_collection(vpm_id):
    # Get the collection
    response = requests.get(f"{base_url}/collections/{vpm_id}")
    if response.status_code == 200:
        collection = response.json()
        return collection
    else:
        # print(f"Failed to get STAC Collection. Response status code: {response.status_code}")
        return None


# FUNCTION 26: THIS IS A FUNCTION TO READ A STAC ITEM
def read_stac_item(vpm_id, cell_id):
    cell_id = f"{cell_id}_{vpm_id}"
    # Send a GET request to your server to read the item
    response = requests.get(f"{base_url}/collections/{vpm_id}/items/{cell_id}")

    if response.status_code == 200:
        # print(f"Successfully read STAC Item with id {cell_id}")
        item_data = response.json()
        return item_data
    else:
        # print(f"Failed to read STAC Item. Response status code: {response.status_code}")
        return None


# FUNCTION 27: THIS IS A FUNCTION TO UPDATE THE STAC COLLECTION BASED ON STAC ITEM/ITEMS
def update_stac_collection(vpm_id):
    # Get all items in the collection
    response = requests.get(f"{base_url}/collections/{vpm_id}/items")
    if response.status_code == 200:
        items = response.json()["features"]
        if len(items) == 0:
            # print("No STAC Items to update the STAC Collection.")
            return
        # If there's only one item, use its bounds
        elif len(items) == 1:
            bbox = items[0]["bbox"]
            datetime_str = items[0]["properties"]["datetime"]
            datetime = [datetime_str, datetime_str]
        # If there's more than one item, compute the minimum and maximum bounds and dates
        else:
            bbox = [
                min(item["bbox"][0] for item in items),
                min(item["bbox"][1] for item in items),
                max(item["bbox"][2] for item in items),
                max(item["bbox"][3] for item in items),
            ]
            datetime = [
                min(item["properties"]["datetime"] for item in items),
                max(item["properties"]["datetime"] for item in items),
            ]

            # Convert them back to strings in ISO 8601 format
            datetime = [dt.replace("Z", "+00:00") for dt in datetime]

        # Get the collection
        response = requests.get(f"{base_url}/collections/{vpm_id}")
        if response.status_code == 200:
            collection = response.json()

            # Store original bounds and datetime
            original_bbox = collection["extent"]["spatial"]["bbox"][0]
            original_datetime = collection["extent"]["temporal"]["interval"][0]

            # Check if an update is required
            if original_bbox == bbox and original_datetime == datetime:
                # print("No Update Required as everything within STAC Collection")
                return None
            else:
                # Update the collection's bounds
                collection["extent"]["spatial"]["bbox"] = [bbox]
                collection["extent"]["temporal"]["interval"] = [
                    [datetime[0], datetime[1]]]

                # Update the collection
                response = requests.put(
                    f"{base_url}/collections", json=collection)
                if response.status_code == 200:
                    print("Successfully updated STAC Collection.")
                else:
                    print(
                        f"Failed to update STAC Collection. Response status code: {response.status_code}")
        else:
            print(
                f"Failed to get STAC Collection. Response status code: {response.status_code}")
    else:
        print(
            f"Failed to get STAC Items. Response status code: {response.status_code}")


# FUNCTION 28: THIS IS A FUNCTION FOR UPDATING STAC ITEMS
def update_stac_item(vpm_id, cell_id, new_asset_paths, original_path):
    cell_id = f"{cell_id}_{vpm_id}"

    # Step 1: Get the STAC Item
    response = requests.get(f"{base_url}/collections/{vpm_id}/items/{cell_id}")
    if response.status_code == 200:
        item_data = response.json()
    else:
        print(
            f"Failed to retrieve STAC Item. Response status code: {response.status_code}")
        return None

    # Initialize a variable to keep track of whether any new assets were added or updated
    asset_updated = False

    for new_asset_path, orig_path in zip(new_asset_paths, original_path):
        file_extension = os.path.splitext(new_asset_path)[1]
        handler = select_handler(file_extension)
        fields = handler(new_asset_path)

        asset_id = generate_asset_id(new_asset_path, fields)
        new_asset = create_asset_from_path(new_asset_path, orig_path)

        if asset_id in item_data["assets"]:
            # If asset with the same SHA-256-based asset ID exists, skip it
            continue
        else:
            # If asset doesn't exist, add the new asset
            item_data["assets"][asset_id] = new_asset.to_dict()
            asset_updated = True

    # Step 3: Update the datetime if a new asset was added or an existing asset was updated
    if asset_updated:
        current_datetime = datetime.now(timezone.utc)
        current_datetime_str = current_datetime.isoformat()
        parsed_datetime = datetime.fromisoformat(
            current_datetime_str.replace("Z", "+00:00"))
        item_data["properties"]["datetime"] = parsed_datetime.isoformat()

        headers = {"Content-Type": "application/json"}
        response = requests.put(f"{base_url}/collections/{vpm_id}/items/{cell_id}",
                                data=json.dumps(item_data),
                                headers=headers)
        if response.status_code == 200:
            print(f"Successfully updated STAC Item with id {cell_id}")
            return True
        else:
            print(
                f"Failed to update STAC Item. Response status code: {response.status_code}")
            return False
    else:
        return None


# FUNCTION 29: THIS IS A FUNCTION TO DELETE A STAC ITEM
def delete_stac_item(vpm_id, cell_id):
    cell_id = f"{cell_id}_{vpm_id}"
    # Send a DELETE request to your server to remove the item
    response = requests.delete(
        f"{base_url}/collections/{vpm_id}/items/{cell_id}")

    if response.status_code == 200:
        print(f"Successfully deleted STAC Item with id {cell_id}")
    else:
        print(
            f"Failed to delete STAC Item. Response status code: {response.status_code}")


# FUNCTION 30: THIS IS A FUNCTION TO DELETE A STAC COLLECTION
def delete_stac_collection(vpm_id):
    # Send a DELETE request to your server to delete the collection
    response = requests.delete(f"{base_url}/collections/{vpm_id}")

    if response.status_code == 200:
        print(f"Successfully deleted STAC Collection with id {vpm_id}")
    else:
        print(
            f"Failed to delete STAC Collection. Response status code: {response.status_code}")


# FUNCTION 31: THIS IS A FUNCTION FOR PRINTING THE COLLECTION ID AND THE ITEM ID WITHIN THE COLLECTIONS
def print_stac_collection_items(vpm_id):
    # get the collection first
    response = requests.get(f"{base_url}/collections/{vpm_id}")
    if response.status_code == 200:
        collection = response.json()
        items_url = ""
        for link in collection["links"]:
            if link["rel"] == "items":
                items_url = link["href"]
                break

        if items_url:
            items_response = requests.get(items_url)
            if items_response.status_code == 200:
                # based on GeoJSON standard
                items = items_response.json()["features"]

                print(f"STAC Collection ID: {vpm_id}")
                print("STAC Item IDs:")
                for item in items:
                    print(item['id'])
            else:
                print(
                    f"Failed to get STAC Items for Collection. Response status code: {items_response.status_code}")
        else:
            print(f"No 'items' link found in the collection: {vpm_id}")
    else:
        print(
            f"Failed to get STAC Collection. Response status code: {response.status_code}")


# FUNCTION 32: THIS IS A FUNCTION FOR PERFORMING THE ENTIRE DATA MANAGEMENT AS PART OF STAC CATALOGING
def stac_catalog(vpm_id, licence, asset_paths, original_path, assets_to_delete=[], delete_collection=[]):
    # Get cell_id from find_smallest_geohash()
    # cell_id = geodata_to_geohash.find_smallest_geohash(asset_paths)
    cell_id = "te"

    # Define constraints for the STAC items
    item_id = f"{cell_id}_{vpm_id}"  # STAC item ID

    # First, check if the Collection with this id already exists
    collection_read = read_stac_collection(vpm_id)

    # Also, check if the Item with this id already exists
    item_read = read_stac_item(vpm_id, cell_id)

    # If STAC Collection is available and delete_collection is True, run delete_stac_collection(vpm_id)
    if collection_read is not None and delete_collection:
        delete_stac_collection(vpm_id)
        print("STAC Collection deleted.")
        # return

    # If STAC Collection is available and STAC item is available and assets_to_delete is true,
    # Then run delete_asset_from_path(vpm_id, cell_id, assets_to_delete) followed by update_stac_collection(vpm_id)
    elif collection_read is not None and item_read is not None and assets_to_delete:
        delete_asset_from_path(vpm_id, cell_id, assets_to_delete)
        update_stac_collection(vpm_id)
        print("Assets deleted and STAC Collection updated.")
        # return [item_id]

    # If both collection and item doesn't exist, create them and update the collection
    elif collection_read is None and item_read is None:
        collection = create_stac_collection(vpm_id, licence,
                                            start_datetime=None,
                                            end_datetime=None,
                                            spatial_extent=None)
        create_stac_item(vpm_id, cell_id, asset_paths, collection, original_path)
        update_stac_collection(vpm_id)
        # return [item_id]

    # If collection is available and item is empty, then create item, and update collection.
    elif collection_read is not None and item_read is None:
        create_stac_item(vpm_id, cell_id, asset_paths, collection_read, original_path)
        update_stac_collection(vpm_id)
        # return [item_id]

    # If both collection and item are available, then run the function for updating the stac item and update the stac collection.
    elif collection_read is not None and item_read is not None:
        update_stac_item(vpm_id, cell_id, asset_paths, original_path)
        update_stac_collection(vpm_id)
        # return [item_id]

    # Print Collection ID and Item IDs
    print_stac_collection_items(vpm_id)

    # Returning a list of [item_id] as the output of this function
    return [item_id]


# End of Python Script
