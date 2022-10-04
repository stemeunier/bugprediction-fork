# Docker command

## Build the image

To build your latest docker image run the following command :

```
docker build -t optittm/bugprediction:latest .
```

## Launch container with this image

Execute **bugprediction** command by using docker thanks to this command on Linux:

```
docker run --rm --name bugprediction -v $(pwd)/data:/home/optittm-user/data optittm/bugprediction <CLI_COMMAND>
```

or on Windows :

```
docker run --rm --name bugprediction -v %cd%/data:/home/optittm-user/data optittm/bugprediction <CLI_COMMAND>
```

## Configurations

The configurations are described in the mounted volume data/.env. You have to copy the default file .env-example in this repository, rename it into .env, and edit this file with your own configurations.

### Examples

#### Populate the database

```
docker run --rm --name bugprediction -v $(pwd)/data:/home/optittm-user/data optittm/bugprediction populate
```

which results in :

```
...
Cloning into 'dbeaver'...
...
```

#### Export a flatten version of the database into a CSV

```
docker run --rm --name bugprediction -v $(pwd)/data:/home/optittm-user/data optittm/bugprediction export --format csv
```

which gives :

```
...
INFO:root:Function export_to_csv took 0.05598839999999994 seconds
```

See the [list of commands](./commands.md) for other options.
