# bootstrap-keycloak-fastapi-postgres

This project servers as a template project for a full stack application containing
the following components:
1. A frontend written in [Bootstrap](https://getbootstrap.com/).
2. A [Keycloak](https://www.keycloak.org/) auth engine handling authentication
   and authorization.
3. A RESTful backend service written in [FastAPI](https://fastapi.tiangolo.com/)
   (i.e. a [Python](https://www.python.org/) application).
4. A [PostgreSQL](https://www.postgresql.org/) database for persisting data.

The intent of this GitHub project is that it can be cloned and modified to get you
quickly up and running for whatever kind of full stack application you need to
implement. The components and libraries used facilitate loose couplings between
things, so it should be easy to replace a component with something else, if you prefer
that. For now, we provide a [Docker](https://www.docker.com/) Compose stack for the
development environment (_do not use this "as is" directly in production!_), but it
should be a fairly easy task translate this to e.g. a [Helm chart](https://helm.sh/)
facilitating a [Kubernetes](https://kubernetes.io/) deployment giving you all the
fancy scalability features etc. of Kubernetes.

## Prerequisites

* Docker and Docker Compose.

Docker and Docker Compose is all you need in order to get the development environment
up and running, but it will probably be nice to have the following installed too for 
local development:
* Python and [Poetry](https://python-poetry.org/) (for dependency management).
* The [npm CLI](https://github.com/npm/cli) for the Bootstrap frontend development
  (most easlily set up with [nvm](https://github.com/nvm-sh/nvm)).

## Getting Started

The development environment can be started with
```
$ docker compose up -d --build
```

This will fire up the entire stack with hot-reloading enabled for both the backend
and the frontend, so changes to the code should be picked up automatically. The
[docker-compose.yml](docker-compose.yml) also contains a
[Traefik](https://traefik.io/traefik/) service serving as a reverse proxy for
the stack. The components of the application can be accessed on these URLs:
* Frontend: [http://localhost:8080/frontend](http://localhost:8080/frontend)
  (log in with `bruce/bruce`).
* Backend: all URL paths under `http://localhost:8080/backend` (see endpoints in
  [main.py](backend/backend/main.py) and
  [endpoints.py](backend/backend/endpoints.py)).
* Keycloak (auth): [http://localhost:8080/auth](http://localhost:8080/auth)
  (log in with `admin/admin`).
* Traefik UI: [http://localhost:8180](http://localhost:8180).

More details can be found in [docker-compose.yml](docker-compose.yml).

## Stack Components

The development [docker-compose.yml](docker-compose.yml) file contains the
following services:

### db
A PostgreSQL DB for storing all data needed by the application.

### db-init
An init container setting up and maintaining the application database tables
using [Alembic](https://alembic.sqlalchemy.org/en/latest/).

### db-init-data
An init container populating the database with some dummy data for
development purposes. The Python library
[SQLAlchemy](https://www.sqlalchemy.org/) is used for the database
communication.

### keycloak
The Keycloak container handling all the authentication and
authorization stuff.

### wait-for-keycloak
An init container waiting for Keycloak to be ready. Other Docker
Compose services needing a running Keycloak instance can depend on
this service to have completed successfully before starting.

### keycloak-init
An init container responsible for configuring Keycloak, e.g.
setting up realms and clients. The configuration of Keycloak is
handled by [Terraform](https://www.terraform.io/) by using this
[Keycloak provider](https://registry.terraform.io/providers/mrparkers/keycloak/latest/docs).

### backend
The FastAPI RESTful backend (REST API written in Python). The
application is running async and
the database communication is also handled by the asyncio facilities
in [SQLAlchemy](https://www.sqlalchemy.org/).

### nginx
An [Nginx](https://nginx.org/en/) web server serving the Bootstrap
frontend. Note that this service is not started by default since
another service (`webpack`) takes care of serving the frontend and
enabling hot-reloading. The service is included for inspiration when
running in production (_note, however, that the configuration used
here is not in anyway optimized for production_). If you wish to test
out the Nginx service, it can be started with the `--profile nginx`
flag.

### webpack
A [Webpack](https://webpack.js.org/) service running the Bootstrap
frontend with hot-reloading enabled, i.e. source code changes will
be picked automatically.

### traefik
A reverse proxy for (some of) the above components. 

## Authentication

Most of the endpoints in the backend are protected and thus require
authentication via the
[openid-connect](https://auth0.com/docs/authenticate/protocols/openid-connect-protocol)
(OIDC) protocol. In practice, this means that you will need an OIDC token
from Keycloak that must be passed along in an `Authorization` header
when calling the backend. An OIDC token can be obtained from Keycloak as follows
(for the user `bruce` created in the realm named `app` by the Terraform code in
the `keycloak-init` container):
```
$ curl -d 'grant_type=password&client_id=app&username=bruce&password=bruce' \
  "http://localhost:8080/auth/realms/app/protocol/openid-connect/token | jq .

{
  "access_token": "eyJhbGciOiJSU...7ZC9Q",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzUxMiI...ss7r-k8w",
  "token_type": "Bearer",
  "not-before-policy": 0,
  "session_state": "6e88088d-b61c-4aee-a032-08d33e35e611",
  "scope": "email profile"
}
```
The `access_token` can be sent in an `Authorization` header to the backend
like this:
```
$ curl -H "Authorization: Bearer eyJhbGciOiJSU...7ZC9Q" "http://localhost:8080/backend/require/auth"
```
which will just respond with a decoded token as an example payload. If the backend
endpoint is called without the authorization header, you will get an HTTP 401
status code.

## Contact

Feel free to create an issue on this GitHub project if you experience any problems.
Pull requests are welcome, but let us discuss matters first via an issue before
making the pull request.

## TODOs
* Think about how to prepare for production
* Add license
