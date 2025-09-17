import paramiko




# Reusable connection details
HOST = "192.168.1.217"
PORT = 22
USERNAME = "uhdt"
PASSWORD = "vipuhdt"

def push_file(local_path, remote_path):
    """Upload a local file to the remote laptop."""
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)

    sftp = transport.open_sftp_client()
    sftp.put(local_path, remote_path)
    print(f"Uploaded {local_path} → {remote_path}")

    sftp.close()
    transport.close()


def pull_file(remote_path, local_path):
    """Download a remote file to the local laptop."""
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)

    sftp = transport.open_sftp_client()
    sftp.get(remote_path, local_path)
    print(f"Downloaded {remote_path} → {local_path}")

    sftp.close()
    transport.close()


# Example usage:
if __name__ == "__main__":
    # Push example
    push_file("README.txt", "/home/uhdt/Downloads/README.txt")

    # Pull example
    pull_file("/home/uhdt/Downloads/README.txt", "local_copy.txt")



'''

# Create Transport object
transport = paramiko.Transport(('192.168.1.144', 22))
transport.connect(username='uhdt', password='vipuhdt')


# Open SFTP session
sftp = transport.open_sftp_client()


# Upload a new file (or overwrite if it exists)
sftp.put('README.txt', '/home/uhdt/Downloads/README.txt')


# Update a file: open in write mode and write new content
with sftp.file('README.txt', 'w') as remote_file:
    remote_file.write("This is updated content.\n")


# Read back to verify update
with sftp.file('README.txt', 'r') as remote_file:
    print(remote_file.read().decode())


# Download file
sftp.get('README.txt', 'local_copy.txt')


# Close connection
sftp.close()
transport.close()

'''


