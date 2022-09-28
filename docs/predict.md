# predict command

Once you have [trained](./train.md) your model, you can predict the number of bugs into the comming release (based on the metrics extracted from ```OTTM_CURRENT_BRANCH```):

    $ python main.py predict --model-name bugvelocity
    Predicted value : 31

See the [list of commands](./commands.md) for other options.
