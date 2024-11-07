# Local Development

## Running with docker-compose for Development

A docker-compose file is available to simplify launching terrareg for local testing and development. This will let you run terrareg with an SSL certificate, allowing terraform cli to access modules while developing or testing the software. In addition, the root folder is mounted in the container allowing for rapid development and testing without rebuilding the container.

Using docker-compose will spin up a stack of containers including:

  * Traefik
  * docker-socket-proxy
  * terrareg
  * mysql
  * phpmyadmin
  * minio (S3 storage)

__*NOTE: Traefik requires exposing the docker socket to the container. Please see [here](https://doc.traefik.io/traefik/providers/docker/#docker-api-access) for more information. This implementation utilizes [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) to limit the exposure*__

### Setup local DevBox shell

This project was prepared with a DevBox shell configuration, which prepares all important tools and configurations for the local development environment. To start the shell, please first copy the `devbox.json.default` file as `devbox.json` and adapt it to your own requirements if necessary. Then start the DevBox with the command below.

```bash
    devbox shell
```

### DevBox macOS 15.n Sequoia issues (official hotfix)

Apple released 6 macOS 15 Sequoia today–and beta users previously reported that this update breaks existing Nix installations by clobbering _nixbld1-4 (because macOS now includes system daemons that use the same UIDs).

On existing installs, this should manifest as an error when you run some Nix commands:

```bash
# https://discourse.nixos.org/t/macos-15-sequoia-update-clobbers-nixbld1-4-users/52223
curl --proto '=https' --tlsv1.2 -sSf -L https://github.com/NixOS/nix/raw/master/scripts/sequoia-nixbld-user-migration.sh | bash -
```

#### Initialize the Project

You will find an EXAMPLE.env file that is used to configure the stack. Copy this to .env and adjust the configuration options as documented below. The key/value pairs in this file are passed as Environment variables to the terrareg container.

Make sure to change the following variables in the .env file before launching:

* SECRET_KEY
* ADMIN_AUTHENTICATION_TOKEN
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY

```bash
    devbox run preflight
    devbox run preflight_mac
    devbox run init_pyenv
    devbox run init_db
```

### Build and test local server with docker-compose

Every change to the [terrareg-code](/terrareg) should lead to a new container image of the application by re-initialising the docker-compose stack, as a build path to the core application has been specified in the compose file instead of a fixed docker image.

```bash
    docker-compose up -d
```

Wait a moment for everything to come online. Terrareg will become available after MySQL comes online. You can then access the stack at the following URLs:

  * terrareg - https://terrareg.app.localhost/
  * phpmyadmin - https://phpmyadmin.app.localhost/
  * traefik - https://traefik.app.localhost

Because everything referencing localhost routes to 172.0.0.1 no special host file entries are required. Please note that all subdomains of the selected `*.app.localhost` domain must have a valid tls certificate. This is generated during the `preflight` phase (`devbox run preflight`) and signed by a local root certificate.

### Build and test local server ***without*** docker-compose

This approach is only used to complete the documentation, we recommend using the docker compose stack (!) for local development on the stack. In this case, an SQLite database is used instead of the mariadb and persistence takes place on a local data mount.

```bash
# Optionally create a virtualenv
virtualenv -ppython3 venv
. venv/bin/activate

# Install libmagic
## For OS X:
brew install libmagic

## For Ubuntu/Debian:
sudo apt-get install libmagic1

# Install minimum dependencies:
pip install -r requirements.txt

# Initialize database & start local server:
alembic upgrade head

# Set random admin authentication token - the password used for authenticating as the built-in admin user
export ADMIN_AUTHENTICATION_TOKEN=MySuperSecretPassword
# Set random secret key, used encrypting client session data
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')

# Run the server
python ./terrareg.py
```

The site can be accessed at http://localhost:5000

## Generating DB changes

Once changes are made to a

```bash
# Ensure database is up-to-date before generating schema migrations
alembic upgrade head

# Generate migration
alembic revision --autogenerate
```

## Applying DB changes

```bash
alembic upgrade head
```

## Running tests

```bash
# Install dev requirements
pip install -r requirements-dev.txt

# Run all tests
pytest

# Running unit-, integration- and selenium tests individually
pytest ./test/unit
pytest ./test/integration
pytest ./test/selenium

# Running a specific test
pytest -k test_setup_page
```

## Build + Check local Application Docker-Image

```bash
# create local docker image for terrareg (t42-local/terrareg:latest, t42-local/terrareg:3.12.2-edp-1)
make build
# check docker image using trivy
make check
```
