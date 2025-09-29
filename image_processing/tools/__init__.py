from exiftool import ExifToolHelper

def extractMetadata(fileName):
    with ExifToolHelper() as et:
        metadata = et.get_metadata(fileName)[0]
    
        if 'EXIF:GPSLatitude' in metadata and 'EXIF:GPSLongitude' in metadata:  
            print('hello')
            latitude = metadata['EXIF:GPSLatitude']
            longitude = -metadata['EXIF:GPSLongitude']  # EXIF default is East, but we are in the West
            altitude = metadata['EXIF:GPSAltitude']
            comment = metadata['File:Comment']
            yaw= float([component.split(":")[1] for component in comment.split() if component.startswith("yaw:")][0])
            pix_width = metadata['File:ImageWidth']
            pix_height = metadata["File:ImageHeight"]
            dpi_resolution = metadata['EXIF:XResolution']
            focal_length = metadata['EXIF:FocalLength']
            return metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length
