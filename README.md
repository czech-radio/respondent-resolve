# cro-respondent-resolve

[![build](https://github.com/czech-radio/cro-respondent-resolve/actions/workflows/main.yml/badge.svg)](https://github.com/czech-radio/cro-respondent-resolve/actions/workflows/main.yml)
![version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![language](https://img.shields.io/badge/language-Python-blue.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73277f30f0ed43daaef0a8cee576cc98)](https://www.codacy.com/gh/czech-radio/cro-respondent-resolve/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=czech-radio/cro-respondent-resolve&amp;utm_campaign=Badge_Grade)

**The web application speeding up the manual identification of respondents from the OpenMedia system.**

*More detail description here.*

## Installation

&hellip;

## Features and Usage

&hellip;

## Development

## How to run backend

To run backend server do:

```shell
source .env/bin/activate
pip install -e .
source .env
cro-respondent-resolve
```

Note the `.env` file, which contains following database connection credentials:

```shell
export AURA_TARGET_HOST=secret
export AURA_TARGET_PORT=secret
export AURA_TARGET_NAME=secret
export AURA_TARGET_USER=secret
export AURA_TARGET_PASS=secret
```

In the browser you then can point to `https://localhost:5000`

An API has (so far) following endpoints:

`/respondents/<year: int>/<week: int>`
Loads xml from R disk to memory and returns as JSON

`/persons`
Loads Aura database entries and returns them as JSON

`/resolved`
returns matching persons (needs prior call `/persons` and `/respondents`)

`/resolved/<year: int>/<week: int>`
runs all above at once and returns persons with matching_ids as JSON

## How to run frontend

&hellip;
