"""Download only the selected official TLC monthly Parquet file (about 48 MB)."""
from pathlib import Path
from urllib.request import urlretrieve
URL='https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
Path('data').mkdir(exist_ok=True)
urlretrieve(URL,'data/yellow_tripdata_2024-01.parquet')
print('Downloaded', URL)
