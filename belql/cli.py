"""Command line interface to BELQL"""

import sys
import json
import logging

import click
import pandas as pd

from belql.run import app
from belql.utils import get_bel_data


logger = logging.getLogger(__name__)


@click.group(help="BELQL test framework Command Line Utilities on {}".format(sys.executable))
@click.version_option()
def main():
    """Entry method."""
    pass


@main.command('serve')
@click.option('-p', '--port', default=5000, help='Port for web server')
@click.option('-h', '--host', default="127.0.0.1", help='Web server host')
def serve(port, host: str):
    """Run the flask web server."""
    app.run(port=port, host=host)


@main.command('query')
@click.argument('subj')
@click.argument('relation')
@click.argument('obj')
@click.argument('output')
@click.option('-d', '--database', default="pharmacome", help="KG to query. Defaults to 'pharmacome'")
@click.option("-k", "--key", default="?", help="Annotation key to filter by")
@click.option("-v", "--value", default="?", help="Annotation value to filter by")
def query(subj: str, relation: str, obj: str, output: str, database: str, key: str, value: str):
    """Query the KG with a BELQL like triple and save to TSV.

    belql query 'p(HGNC:"MAPT")' causal ? output.tsv
    """
    stmt = f'{subj.strip()} {relation.strip()} {obj.strip()}'
    context = get_bel_data(stmt, database=database, anno_key=key, anno_val=value)
    datadict = json.loads(context)
    df = pd.DataFrame(datadict["data_rows"], columns=datadict["column_names"])
    df.to_csv(output, sep="\t", index=False)
