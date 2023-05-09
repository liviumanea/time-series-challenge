import logging
import sys
import time
from contextlib import contextmanager
from os import getenv
from typing import ContextManager

import pandas as pd
import requests
from influxdb_client import InfluxDBClient, WritePrecision, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(level=logging.INFO)

_logger = logging.getLogger(__name__)


@contextmanager
def connect(url: str, token: str) -> ContextManager[WriteApi]:
    with InfluxDBClient(url=url, token=token) as client:
        yield client.write_api(write_options=SYNCHRONOUS)


def load() -> pd.DataFrame:
    # Read input data
    assets_file = "data/assets.json"
    assets = pd.read_json(assets_file)
    signals_file = "data/signal.json"
    signals = pd.read_json(signals_file)
    signals = signals.drop(columns=['SignalGId'], axis=1)
    asset_signals = pd.merge(signals, assets, left_on='AssetId', right_on='AssetID')
    asset_signals = asset_signals.drop(columns=['AssetID', 'Latitude', 'Longitude', 'descri', 'SignalName'])

    csv_file = "data/measurements.csv"
    measurements = pd.read_csv(csv_file, sep="|", thousands=',')
    measurements['Ts'] = pd.to_datetime(measurements['Ts'])
    # join al the measurement, signal and asset data
    measurements = pd.merge(measurements, asset_signals, left_on='SignalId', right_on='SignalId')
    return measurements


def wait_for_resource(url: str, timeout: int = 120) -> bool:
    start_time = time.time()

    while time.time() - start_time < timeout:
        _logger.debug(f"Waiting for {url} to become available...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(5)

    _logger.error(f"Resource is not available within the given timeout ({timeout}s).")
    return False


def main(
        influx_url: str,
        influx_token: str,
        influx_org: str,
        influx_bucket: str
):
    _logger.debug("Loading measurements...")
    measurements = load()

    _logger.debug("Ingesting measurements...")
    with connect(influx_url, influx_token) as write_api:
        # isolate the measurements per unit type and ingest
        for unit in measurements['Unit'].unique():
            data = measurements[measurements['Unit'] == unit].drop(
                columns=['Unit']
            ).rename(columns={'MeasurementValue': unit})
            write_api.write(
                bucket=influx_bucket,
                org=influx_org,
                record=data,
                write_precision=WritePrecision.NS,
                data_frame_timestamp_column="Ts",
                data_frame_measurement_name=unit,
                data_frame_tag_columns=["SignalId", "SignalName", "AssetId"]
            )
    _logger.info("Ingestion complete.")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    iflux_url = getenv("APP_INFLUXDB_URL")
    iflux_token = getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
    iflux_org = getenv("DOCKER_INFLUXDB_INIT_ORG")
    iflux_bucket = getenv("DOCKER_INFLUXDB_INIT_BUCKET")

    _logger.debug("Connecting to InfluxDB...")
    if not wait_for_resource(iflux_url):
        _logger.error("InfluxDB is not available.")
        sys.exit(1)

    main(iflux_url, iflux_token, iflux_org, iflux_bucket)
    _logger.debug("Done.")
