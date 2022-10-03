# Docker command

## Build the image

To build your latest docker image run the following command :

```
docker build -t optittm/bugprediction:latest .
```

## Launch container with this image

Execute **optittm/bugprediction** command by using docker thanks to this command :

```
docker run --rm --name bugprediction optittm/bugprediction <CLI_COMMAND>
```

See the [list of commands](./commands.md) for other options.
