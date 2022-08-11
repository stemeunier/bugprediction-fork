# ![logo](https://raw.githubusercontent.com/optittm/bugprediction/main/logo.png) Bug Prediction
 Generate a dataset for benchmarking bug prediction models

## Introduction

Our intend is to create a tool that automatically generates a comprehensive dataset for testing bug prediction model. 
The first prototype will target Java based projects hosted on GitHub.

The tool will connect to a GitHub repository and fecth releases, code history, and issues.
For each release the tool will:
 - Checkout the code and run static analysis tools to build metrics (e.g. cyclomatic complexity, object coupling, etc.)
 - Analyze the declared issues and compute metrics such as bug velocity
 - Exploit git log so as to build metrics related to churn, team seniority, etc.
 - Compute metrics from a curated list of academic papers.
 
We hope that you will find this tool helpful for benchmarking your model.
