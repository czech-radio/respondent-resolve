# cro-respondent-resolve

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f43bda46fab747159b2144da084da2c0)](https://app.codacy.com/gh/czech-radio/cro-respondent-resolve?utm_source=github.com&utm_medium=referral&utm_content=czech-radio/cro-respondent-resolve&utm_campaign=Badge_Grade_Settings)

About&hellip;

## Install

...

## Usage

...

## how to run backend


To run backend server do:

```
source .env/bin/activate
pip install -e .
source .env
cro-respondent-resolve
```

note the `.env` file, which contains following DB connection details:

```
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
