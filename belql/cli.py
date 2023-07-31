"""Command line interface to BELQL"""

import sys
import logging

import click
from tabulate import tabulate

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
@click.option('-d', '--database', default="pharmacome", help="KG to query. Defaults to 'pharmacome'")
def query(subj: str, relation: str, obj: str, database: str):
    """Query the KG with a BELQL like triple."""
    stmt = f'{subj.strip()} {relation.strip()} {obj.strip()}'
    context = get_bel_data(stmt, database=database)
    click.echo(tabulate(context, headers='keys', tablefmt='psql'))
