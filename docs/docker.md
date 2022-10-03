# Docker command

## Build the image

To build your latest docker image run the following command :

```
docker build -t optittm/bugprediction:latest .
```

## Launch container with this image

Execute **optittm/bugprediction** command by using docker thanks to this command on Linux:

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
INFO:root:python: 3.10.7
INFO:root:system: Linux
INFO:root:machine: x86_64
INFO:root:created temporary directory: /tmp/tmpqvp3g4a5
Cloning into 'dbeaver'...
...
```

#### Export a flatten version of the database into a CSV

```
docker run --rm --name bugprediction -v $(pwd)/data:/home/optittm-user/data optittm/bugprediction export --format csv
```

which gives :

```
INFO:root:python: 3.10.7
INFO:root:system: Linux
INFO:root:machine: x86_64
INFO:root:export
INFO:root:export_to_csv
DEBUG:root:SELECT version.version_id, version.project_id, version.name, version.tag, version.start_date, version.end_date, version.bugs, version.changes, version.avg_team_xp, version.bug_velocity, metric.metrics_id, metric.version_id AS version_id_1, metric.cloc_text_files, metric.cloc_unique_files, metric.cloc_ignored_files, metric.cloc_files, metric.cloc_blank, metric.cloc_comment, metric.cloc_code, metric.lizard_total_nloc, metric.lizard_avg_nloc, metric.lizard_avg_token, metric.lizard_fun_count, metric.lizard_fun_rt, metric.lizard_nloc_rt, metric.lizard_total_complexity, metric.lizard_avg_complexity, metric.lizard_total_operands_count, metric.lizard_unique_operands_count, metric.lizard_total_operators_count, metric.lizard_unique_operators_count, metric.total_lines, metric.total_blank_lines, metric.total_comments, metric.comments_rt, metric.ck_cbo, metric.ck_cbo_modified, metric.ck_fan_in, metric.ck_fan_out, metric.ck_dit, metric.ck_noc, metric.ck_nom, metric.ck_nopm, metric.ck_noprm, metric.ck_num_fields, metric.ck_num_methods, metric.ck_num_visible_methods, metric.ck_nosi, metric.ck_rfc, metric.ck_wmc, metric.ck_loc, metric.ck_lcom, metric.ck_lcom_modified, metric.ck_tcc, metric.ck_lcc, metric.ck_qty_returns, metric.ck_qty_loops, metric.ck_qty_comparisons, metric.ck_qty_try_catch, metric.ck_qty_parenth_exps, metric.ck_qty_str_literals, metric.ck_qty_numbers, metric.ck_qty_math_operations, metric.ck_qty_math_variables, metric.ck_qty_nested_blocks, metric.ck_qty_ano_inner_cls_and_lambda, metric.ck_qty_unique_words, metric.ck_numb_log_stmts, metric.ck_has_javadoc, metric.ck_modifiers, metric.ck_usage_vars, metric.ck_usage_fields, metric.ck_method_invok, metric.jp_camc, metric.jp_lcom, metric.jp_mmac, metric.jp_nhd, metric.jp_scom, metric.halstead_length, metric.halstead_vocabulary, metric.halstead_volume, metric.halstead_difficulty, metric.halstead_effort, metric.halstead_time, metric.halstead_bugs
FROM version JOIN metric ON metric.version_id = version.version_id
WHERE version.project_id = :project_id_1
INFO:root:Function export_to_csv took 0.05598839999999994 seconds
```

See the [list of commands](./commands.md) for other options.
