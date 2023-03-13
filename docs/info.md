# info command

The info command provides basic information about the project configured into the ```.env``` file.

    $ python main.py info
     -- OTTM Bug Predictor --
        Project  : jpeek
        Language : Java
        SCM      : github / https://github.com/cqfn/jpeek
        Release  : master
        
        Versions : 66
        Issues   : 530
        Metrics  : 66
    
        Trained models : bugvelocity

It can be useful to quickly validate your current configuration and the content of the database.

See the [list of commands](./commands.md) for other options.
