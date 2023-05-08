# Time series challenge

## Introduction

We are required to process and represent time series data provided in the `data` directory as detailed in the 
original `README.assignment.md` file.

The project specifications are presented with a high degree of flexibility, suggesting that we are in the initial 
stages of formulating a solution. As there are no stringent requirements regarding the choice of tools or the 
intricacies of the full-stack application, I have opted to focus on data ingestion using Python from the supplied 
static files. 

This approach streamlines the process by leveraging the well-established and high-quality tools, InfluxDB and Grafana,
which are renowned for their effectiveness in handling time series data and align with the anticipated direction of the
application. By adopting this strategy, we maintain flexibility, allowing us to postpone critical decisions that might
be difficult to modify later until we gain a more comprehensive understanding of the requirements such as optimum
ingestion mechanisms accounting for data volume. 

Furthermore, this tactic provides us with the opportunity to potentially utilize the existing technology stack as
it stands, if deemed suitable.

## Solution overview

The solution comprises three main components:
- Data ingestion using the python script provided in the `ingestion` directory.
- Data storage using InfluxDB.
- Data visualization using Grafana.

Deployment is achieved using Docker Compose, which orchestrates the containers and injects configuration for the
entire stack from the sample `.env` file which is included in the repository for convenience.

### Grafana

The Grafana service is conveniently pre-configured with the necessary data sources and dashboards, 
enabling seamless connectivity to the InfluxDB database and effortless visualization of the associated graphs.

The pertinent files for Grafana provisioning can be found in the `grafana` directory and are mounted into the 
container through the utilization of docker-compose, ensuring a smooth integration process.


### Ingestion script

The Python-based ingestion script, situated in the ingestion directory, is specifically crafted to function as a 
one-time process, handling and incorporating data from the provided files into the InfluxDB database.

Moreover, the ingestion script incorporates a feature that enables it to delay execution until the InfluxDB service
becomes accessible, ensuring a well-timed and orderly data ingestion process.

The script's dependencies are managed utilizing `pip-tools`, with the specifications detailed in the 
`ingestion/requirements.in` file.

Docker Compose automatically constructs the image for this service, employing the `Dockerfile.ingestion` file.


## Usage

Upon cloning the project locally, simply execute `docker-compose up` from the root directory to initiate the stack.

Following the retrieval or construction of the necessary images, the ingestion script will be executed, 
making the data accessible.

To visualize the graphs, visit http://localhost:3000 and log in using the username `admin` and password `secret` as
configured in the sample configuration file `.env`.

The dashboard can be found under `Dashboards > Services > IOT Energy`.