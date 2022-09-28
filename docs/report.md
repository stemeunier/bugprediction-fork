# report command

The tool can genrate an offline report (doesn't need any external Internet access):

    python main.py report --output .

Of course, you need to [populate](./populate.md) the database in order to fill the metrics. And if no model is [trained](./train.md) the predicted values will not be part of the report.

See the [list of commands](./commands.md) for other options.
