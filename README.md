# ![logo](https://raw.githubusercontent.com/optittm/bugprediction/main/logo.png) Bug Prediction

An experimental tool to compile code metrics (static analysis) from a project hosted on a git repository.
The objective is to automatically build a comprehensive dataset. This dataset will benchmark bug prediction machine learning models.

## Introduction

Our objective is to create a tool that automatically generates a comprehensive dataset for testing bug prediction models. 
The first prototype will target Java based projects hosted on GitHub.

The tool will connect to a SCM repository and fecth releases, code history, and issues.
For each release the tool will:
 - Checkout the code and run static analysis tools to build metrics (e.g. cyclomatic complexity, object coupling, etc.)
 - Analyze the declared issues and compute metrics such as bug velocity
 - Exploit git log so as to build metrics related to churn, team seniority, etc.
 - Compute metrics from a curated list of tools and academic papers.
 
We hope that you will find this tool helpful for benchmarking your model.

## Usage

The tool needs to target a repository with release. In the opposite, you need to import them into the version table.
## Tools

### General

 - Lizard : https://github.com/terryyin/lizard
 - CodeMaat : https://github.com/adamtornhill/code-maat

### Java

 - CK : https://github.com/mauricioaniche/ck
 - JPeek : https://github.com/cqfn/jpeek
