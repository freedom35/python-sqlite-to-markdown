# SQLite Results to Markdown
This repo contains a Python app to export the results of a SQLite query to a markdown file.

This software may be used/updated under the terms of the **MIT license**.  

## Requirements
* [Python 3](https://www.python.org/downloads/)

## Usage
The app is expecting the following command line args:

|Arg|Description|
|---|---|
|1<sup>st</sup>|Path to SQLite database file|
|2<sup>nd</sup>|Path to SQL file containing source query|
|3<sup>rd</sup> (Optional)|Directory where markdown file will be created|

Note: The markdown file created will have the same filename as the input sql file, but with the extension changed to **md**.

Example:
```sh
$ python3 exportmd.py sample.db query.sql
```

In this case, a *query.md* file with the results will be created in the current directory - the same directory as the *query.sql* file.

Example with optional export directory:
```sh
$ python3 exportmd.py sample.db query.sql export-data
```

In this case, a *query.md* file with the results will be created in the *export-data* directory.

## Markdown File
The contents of the markdown file will depend on the query file and the results it produces. The markdown file will contain the following:

1. A heading based on query filename.
2. If the query file contains any SQL comments at the top of the file, these will be exported to the markdown file.
3. The query results will be converted to a markdown table, with the field names being used as the table headings.

An example of the output format is shown below:

```
# query-filename-without-ext

Optional comment(s) from start of query file.

|ID|Value|
|:-:|---|
|1|Value A|
|2|Value B|

```

Note: Numeric fields will be center aligned, normal text will be left aligned.