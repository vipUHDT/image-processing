from exiftool import ExifToolHelper
import multiprocessing
import subprocess

def extractMetadata(file_name):
    with ExifToolHelper() as et:
        metadata = et.get_metadata(file_name)[0]
        # print(metadata['File:Comment'])
        if 'EXIF:GPSLatitude' in metadata and 'EXIF:GPSLongitude' in metadata:  
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
        
def execute(command):
    subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
     
def embedMetadata(file_name, latitude, longitudate, pitch, yaw, roll):
        orientation = f"pitch: {pitch} yaw: {yaw} roll: {roll}"
        
        embed_orientation_command = ('exiftool','-overwrite_original', f'-comment={orientation}', file_name)
        embed_latitude_command = ('exiftool','-overwrite_original', '-exif:gpslatitude=\'{latitude}', file_name)
        embed_longitude_command = ('exiftool','-overwrite_original', '-exif:gpslongitude=\'{longitude}', file_name)
        embed_altitude_command = ('exiftool','-overwrite_original', '-exif:gpsaltitude=\'{altitude}', file_name)

        embed_commands = [embed_orientation_command, embed_latitude_command, embed_longitude_command, embed_altitude_command]
        
        for command in embed_commands:
            multiprocessing.Process(target = execute, args = (command,))

