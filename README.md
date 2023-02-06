# ![logo](https://raw.githubusercontent.com/optittm/bugprediction/main/logo.png) Bug Prediction

*bugprediction* compile data from a SCM server (e.g. github), static code analysis, and optional manual import (e.g. issues, releases). It can provide an offline HTML report about the assessment of the risk of delivering the next release. It can be usefull for datascientists who wants to benchmark bug prediction machine learning models.

## Introduction

The tool will connect to a SCM repository and fecth releases, code history, and issues.
For each release the tool will:
 - Checkout the code and run static analysis tools to build metrics (e.g. cyclomatic complexity, object coupling, etc.)
 - Analyze the issues and compute metrics such as bug velocity
 - Analyze git log so as to build metrics related to churn, team seniority, etc.
 - Compute metrics from a curated list of tools and academic papers.

## Usage

The tool needs to target a repository (e.g. GitHub, GitLab) with releases and issues. If you use another tool, you'd need to import releases and issues into the database.

You need to create and ```data/.env``` file (by copying the ```.env-example```) and to fill at least these variables (see the [documentation of populate command](./docs/commands.md) for) :

 - ```OTTM_SCM_PATH``` : Path to git executable, leave "git" if it's into system env. path
 - ```OTTM_SOURCE_PROJECT``` : Name of the project (e.g. dbeaver)
 - ```OTTM_SOURCE_REPO``` : Repositiory name (e.g. dbeaver/dbeaver)
 - ```OTTM_CURRENT_BRANCH``` :  The branch containing the next release (e.g. devel)
 - ```OTTM_SOURCE_REPO_URL``` : # The full path to repo (e.g. https://github.com/dbeaver/dbeaver)
 - ```OTTM_SOURCE_BUGS``` : Source where we get issues (e.g. git)
 - ```OTTM_SOURCE_REPO_SCM``` : Either "github" or "gitlab", other SCM are not yet supported
 - ```OTTM_SCM_BASE_URL``` : SMC base URL - leave empty for public repo
 - ```OTTM_SCM_TOKEN``` : Token to access github or gitlab
 - ```OTTM_TARGET_DATABASE``` : The default value will generate a SQLite database into the current folder
 - ```OTTM_ISSUE_TAGS``` : On bug reporting tools, you can filter issues by tags. You can specify multiples tags, comma separated.
 - ```OTTM_JIRA_BASE_URL``` : The full path to jira project (e.g. https://jira.atlassian.com)
 - ```OTTM_JIRA_PROJECT``` :  Jira project identifier
 - ```OTTM_JIRA_EMAIL``` : Jira user email address. To access Jira API, you need to provide your access tokend AND your email adress
 - ```OTTM_JIRA_TOKEN``` : Token to access jira
 - ```OTTM_JIRA_ISSUE_TYPE```: When Jira is used as the bug reporting tool, you can filter issues by their issue type. You can specify several filters, comma separeted. Usually, bugs are repported on "Bug" issue type.
 
 The first step (it might take a while) is to populate the database with versions, issues and commits. The repository will be cloned into a temporary folder and we will checkout all versions in order to generate code metrics. You can run this command in many times as it will only amend the database with latest changes.

    python main.py populate

The tool is shipped with two simple bug prediction models. You need to train each model before you can use it:

    python main.py train --model-name bugvelocity

And then use it to predict the number of bugs into the comming release (based on the metrics extracted from ```OTTM_CURRENT_BRANCH```):

    $ python main.py predict --model-name bugvelocity
    Predicted value : 31

You can generate an offline HTML report:

    $ python main.py report 

One of the features of the report is to assess the risk of releasing the next version of your project:

![risk assessment gauge](https://raw.githubusercontent.com/optittm/bugprediction/main/docs/images/gauge_risk.png)

See the [list of commands](./docs/commands.md) for other options.

## Limitations

The tool currently doesn't support repositories with multiple releases in parallel (i.e. a latest version maintained in parallel of a LTS version). You have to [import](./docs/import.md) the branch of versions that you want to examine.

Linking issues and commits to a version is a tedious task. At this stage, the tool roughly estimate that issues and commits are linked to a version if the objects were created between the start and and dates of the version. 

## Contribute

The tool is released under a MIT licence. Contributors are welcomed in many areas (imporve the tool, add your own model, add a more clever Git tree exploration algo, etc.).
## Tools

### General

 - PyDriller: https://github.com/ishepard/pydriller
 - Lizard: https://github.com/terryyin/lizard
 - CodeMaat: https://github.com/adamtornhill/code-maat

### Java

 - CK: https://github.com/mauricioaniche/ck
 - JPeek: https://github.com/cqfn/jpeek
