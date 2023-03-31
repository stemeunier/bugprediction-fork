# ![logo](https://raw.githubusercontent.com/optittm/bugprediction/main/logo.png) Bug Prediction

*bugprediction* compiles data from a SCM server (e.g. github), static code analysis, and optional manual import (e.g. issues, releases). It can provide an offline HTML report about the assessment of the risk of delivering the next release. It can be useful for datascientists who want to benchmark bug prediction machine learning models.

## Introduction

The tool will connect to a SCM repository and fetch releases, code history, and issues.
For each release the tool will:
 - Check the code out and run static analysis tools to build metrics (e.g. cyclomatic complexity, object coupling, etc.)
 - Analyze the issues and compute metrics such as bug velocity
 - Analyze git logs so as to build metrics related to churn, team seniority, etc.
 - Compute metrics from a curated list of tools and academic papers.

## Usage

The tool needs to target a repository (e.g. GitHub, GitLab) with releases and issues. If you use another tool, you'd need to import releases and issues into the database.

You need to run this commnand to install all the dependencies :
    
    pip install -r requirements.txt


For testing, you can use either the DBeaver project or the much lighter (less time to load) fx2048 project.
Or you can look for any opensource Java project with releases and issues.

You need to create a file in the project directory called ```.env```, you should copy the ```.env-example``` file and fill it with at least these variables (see the [documentation of populate command](./docs/commands.md) for) :

 - ```OTTM_SCM_PATH``` : Path to git executable, leave "git" if it's into system env. path
 - ```OTTM_SOURCE_PROJECT``` : Name of the project (e.g. dbeaver or fx2048 or python-fire)
 - ```OTTM_SOURCE_REPO``` : Repositiory name (e.g. dbeaver/dbeaver or brunoborges/fx2048 or google/python-fire)
 - ```OTTM_CURRENT_BRANCH``` :  The branch containing the next release (e.g. devel for dbeaver or master for fx2048 and python-fire)
 - ```OTTM_SOURCE_REPO_URL``` : # The full path to repo (e.g. https://github.com/dbeaver/dbeaver or https://github.com/brunoborges/fx2048 or https://github.com/google/python-fire)
 - ```OTTM_SOURCE_BUGS``` : Source where we get issues (e.g. git, jira or glpi)
 - ```OTTM_SOURCE_REPO_SCM``` : Either "github" or "gitlab", other SCM are not yet supported
 - ```OTTM_SCM_BASE_URL``` : SCM base URL - leave empty for public repo
 - ```OTTM_SCM_TOKEN``` : Token to access github or gitlab (see the "How to get your tokens" section)
 - ```OTTM_TARGET_DATABASE``` : The default value will generate a SQLite database into the current folder: sqlite:///data/${OTTM_SOURCE_PROJECT}.sqlite3
 - ```OTTM_ISSUE_TAGS``` : On bug reporting tools, you can filter issues by tags. You can specify multiples tags, comma separated. - you can leave it empty
  - ```OTTM_LANGUAGE```: The language of the source repo ("Java" for dbeaver or fx2048, "Python" for python-fire)

If you use Jira, you can fill the next variables, otherwise leave them by default :

 - ```OTTM_JIRA_BASE_URL``` : The full path to jira project (e.g. https://jira.atlassian.com)
 - ```OTTM_JIRA_PROJECT``` :  Jira project identifier
 - ```OTTM_JIRA_EMAIL``` : Jira user email address. To access Jira API, you need to provide your access tokend AND your email adress
 - ```OTTM_JIRA_TOKEN``` : Token to access Jira (see the "How to get your tokens" section)
 - ```OTTM_JIRA_ISSUE_TYPE```: When Jira is used as the bug reporting tool, you can filter issues by their issue type. You can specify several filters, comma separeted. Usually, bugs are repported on "Bug" issue type.

If you use GLPI, you can fill the next variables, otherwise leave them by default :

 - ```OTTM_GLPI_CATEGORIES``` : Categories of Glpi tickets. Only the child categories has to be precised.
 - ```OTTM_GLPI_BASE_URL``` : The full path to glpi API (e.g. http://localhost/apirest.php/)
 - ```OTTM_GLPI_APP_TOKEN``` : Glpi app token
 - ```OTTM_GLPI_USER_TOKEN``` : Glpi user token. To acces GLPI API, you have to chose between using user token, or basic auth login/password
 - ```OTTM_GLPI_USERNAME``` : Glpi username
 - ```OTTM_GLPI_PASSWORD``` : Glpi password
 
 The first step (it might take a while) is to populate the database with versions, issues and commits. The repository will be cloned into a temporary folder and it will check all versions out in order to generate code metrics. You can run this command multiple times later on as it will only amend the database with latest changes.

    python main.py populate

The tool is shipped with two simple bug prediction models. You can train the model that you want.

BugVelocity is a simple Machine Learning model (a bit naive) based on the history of bug velocity values. It demonstrates how you can integrate your own model into the tool.

    python main.py train --model-name bugvelocity

CodeMetrics TODO add explanation

    python main.py train --model-name codemetrics
    
And then use it to predict the number of bugs into the coming release (based on the metrics extracted from ```OTTM_CURRENT_BRANCH```):

    $ python main.py predict --model-name bugvelocity
    Predicted value : 31
or :

    $ python main.py predict --model-name codemetrics
    Predicted value : 31

You can generate an offline HTML report:

    $ python main.py report 
The report will be placed in the './data/export' folder.
One of the features of the report is to assess the risk of releasing the next version of your project:

![risk assessment gauge](https://raw.githubusercontent.com/optittm/bugprediction/main/docs/images/gauge_risk.png)

See the [list of commands](./docs/commands.md) for other options.

## How to get your tokens

These tokens allow Bugprediction to call the apps' APIs and retrieve necessary data. Here's how to get each one of them.
### GitHub
Go into your account's settings -> Developer settings -> Personal access tokens -> Tokens (classic)
Generate a new token (classic):
- Name it however you wish
- Set the expiration depending on your use case
- Don't select any scope
- Generate
Copy the token and paste it next to ```OTTM_SCM_TOKEN``` in the .env file.

### GitLab
Go into Edit profile/User settings -> Access Tokens
Add a new token:
- Name it however you wish
- Set the expiration depending on your use case
- Don't select any scope
- Create
Copy the token and paste it next to ```OTTM_SCM_TOKEN``` in the .env file.

### Jira
Go to your profile's settings page
- Click on "Generate new API token" in the "API token" section.
- Give your token a name and click on "Create".
Copy the token and paste it next to ```OTTM_JIRA_TOKEN``` in the .env file.

## Limitations

The tool currently doesn't support repositories with multiple releases in parallel (i.e. a latest version maintained in parallel of a LTS version). You have to [import](./docs/import.md) the branch of versions that you want to examine.

Linking issues and commits to a version is a tedious task. At this stage, the tool roughly estimate that issues and commits are linked to a version if the objects were created between the start and end dates of the version. 

## Contribute

The tool is released under a MIT licence. Contributors are welcomed in many areas (improve the tool, add your own model, add a cleverer Git tree exploration algo, etc.).
## Tools

### General

 - PyDriller: https://github.com/ishepard/pydriller
 - Lizard: https://github.com/terryyin/lizard
 - CodeMaat: https://github.com/adamtornhill/code-maat

### Java

 - CK: https://github.com/mauricioaniche/ck
 - JPeek: https://github.com/cqfn/jpeek

 ### Python
 - Radon: [https://pypi.org/project/radon/](https://pypi.org/project/radon/)
