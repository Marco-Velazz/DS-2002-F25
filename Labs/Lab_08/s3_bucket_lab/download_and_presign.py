import urllib.request
import boto3

FILE_URL = "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif"
LOCAL_FILENAME = "downloaded.gif"
BUCKET_NAME = "ds2002-f25-pyf7aw"
OBJECT_NAME = "downloaded.gif"
EXPIRES_IN = 3600

def main():
	# Download the file
	print("Downloading from the internet...")
	urllib.request.urlretrieve(FILE_URL, LOCAL_FILENAME)
	print(f"Saved to {LOCAL_FILENAME}")

	# Upload to S3
	s3 = boto3.client("s3")
	print(f"Uploading {LOCAL_FILENAME} to bucket '{BUCKET_NAME}' as '{OBJECT_NAME}'...")
	s3.upload_file(LOCAL_FILENAME, BUCKET_NAME, OBJECT_NAME)

	# Generate a presigned URL
	print("Generating presigned URL...")
	url = s3.generate_presigned_url(
		"get_object",
		Params={"Bucket": BUCKET_NAME, "Key": OBJECT_NAME},
		ExpiresIn=EXPIRES_IN,
	)

	# Output the URL
	print("Presigned URL:")
	print(url)

if __name__ == "__main__":
	main()


