# OTTM Code Metrics Generator

An experimental tool to compile code related metrics from a project hosted on a git repository.
The objective is to automatically build a comprehensive dataset. This dataset will benchmark bug prediction models.


--csv

==========================================================================================
Total nloc   Avg.NLOC  AvgCCN  Avg.token   Fun Cnt  Warning cnt   Fun Rt   nloc Rt
------------------------------------------------------------------------------------------
    463821       8.8     2.4       58.4    39009          530      0.01    0.13

java -jar ck-x.x.x-SNAPSHOT-jar-with-dependencies.jar <project dir> <use jars:true|false> <max files per partition, 0=automatic selection> <variables and fields metrics? True|False> <output dir> [ignored directories...]

Generate git log for code maat

          git log --all --numstat --date=short --pretty=format:'--%h--%ad--%aN' --no-renames --after=YYYY-MM-DD > gitlogfile.log

java -jar ./ext-tools/code-maat-1.0.2.jar -l gitlogfile.log -c git2  > code-maat-verbose.csv
java -jar ./ext-tools/code-maat-1.0.2.jar -l gitlogfile.log -c git2 -a summary > code-maat-summary.csv
java -jar ./ext-tools/code-maat-1.0.2.jar -l gitlogfile.log -c git2 -a abs-churn > code-maat-abs-churn.csv


-a abs-churn

CK Usage :
java -jar ./ext-tools/ck-0.7.1.jar /tmp/dbeaver .
class.csv
field.csv
method.csv
variable.csv

to be tested https://github.com/cqfn/jpeek

Use a .env file
https://www.python-engineer.com/posts/dotenv-python/

Introduction to 