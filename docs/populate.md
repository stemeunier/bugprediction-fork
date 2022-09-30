# populate command

The first step (it might take a while) is to populate the database with versions, issues and commits. The repository will be cloned into a temporary folder and we will checkout all versions in order to generate code metrics. You can run this command in many times as it will only amend the database with latest changes.

    python main.py populate

The tool relies on the environnement variables.

## Sample .env file

See [GitHub documentation](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to see how to create your own personal token.

For analyzing the JPeek project:

```
OTTM_CODE_MAAT_PATH=./ext-tools/code-maat-1.0.2.jar
OTTM_CODE_CK_PATH=./ext-tools/ck-0.7.1.jar
OTTM_CODE_JPEEK_PATH=./ext-tools/jpeek-0.30.25.jar
OTTM_SMC_PATH=git
OTTM_SOURCE_PROJECT=jpeek
OTTM_SOURCE_REPO=cqfn/jpeek
OTTM_CURRENT_BRANCH=master
OTTM_SOURCE_REPO_URL=https://github.com/cqfn/jpeek
OTTM_SOURCE_REPO_SMC=github
OTTM_SMC_BASE_URL=
OTTM_SMC_TOKEN=   <<<Put your own token>>>
OTTM_TARGET_DATABASE=sqlite:///${OTTM_SOURCE_PROJECT}.sqlite3
OTTM_ISSUE_TAGS=
OTTM_EXCLUDE_ISSSUERS=bot,dependabot[bot],synk,gitter-badger
OTTM_EXCLUDE_VERSIONS=
OTTM_INCLUDE_VERSIONS=
OTTM_EXCLUDE_FOLDERS=
OTTM_INCLUDE_FOLDERS=src/main/java/org/jpeek/
OTTM_ISSUE_TAG=
OTTM_LANGUAGE=Java

```

See the [list of commands](./commands.md) for other options.
