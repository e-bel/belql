# BELQL

## Install the Package
BELQL can be installed from PyPI:
```bash
pip install belql
```

## Usage
### CLI
One can use the CLI after installation to directly query the database with your own 
pseudo-BEL statement
```bash
belql query 'p(HGNC:"MAPT")' causal ? --database pharmacome
```
It is advised to encapsulate string in single quotes to ensure it works.

### Run the Web Server
Users can start the server either by running the script directly
```bash
python belql/run.py
```
or via the CLI
```bash
belql serve -p 5000 -h 127.0.0.1
```
The web application is created using Flask and once server is started, 
users can go to http://127.0.0.1:5000/ in their browser.