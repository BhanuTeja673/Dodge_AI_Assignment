import gdown
import os
import zipfile

url = 'https://drive.google.com/uc?id=1UqaLbFaveV-3MEuiUrzKydhKmkeC1iAL'
output = 'data/dataset.zip'

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists(output):
    print(f"Downloading dataset from {url}...")
    gdown.download(url, output, quiet=False)
else:
    print(f"{output} already exists.")

if os.path.exists(output) and output.endswith('.zip'):
    print("Extracting dataset...")
    with zipfile.ZipFile(output, 'r') as zip_ref:
        zip_ref.extractall('data')
    print("Dataset extracted successfully.")
