"""Utility functions for querying the OrientDB database."""

import json
import requests
import pandas as pd

from requests.utils import requote_uri
import urllib.parse


class ApiClient:
    """Parent class for connecting to a BEL graph database and querying it."""

    def __init__(
            self,
            user: str = "guest",
            password: str = "guest",
            host: str = "https://graphstore.scai.fraunhofer.de",
            database: str = "pharmacome",
            ssf: str = "bikmi_belish_edge_anno"
    ):
        self.user = user
        self.__password = password
        self.host = host
        self.database = database
        self.ssf = ssf

        self.url_template = f"{self.host}/function/{self.database}/{self.ssf}/{{bq}}"

        self._data = None

    def connect(
            self,
            database: str | None = None,
            user: str | None = None,
            password: str | None = None,
            host: str | None = None,
            ssf: str | None = None,
    ):
        """Change the connection configuration. Only the passed parameters will be altered."""
        self.user = user if user else self.user
        self.__password = password if password else self.__password
        self.host = host if host else self.host
        self.database = database if database else self.database
        self.ssf = ssf if ssf else self.ssf
        self.url_template = f"{self.host}/function/{self.database}/{self.ssf}/{{bq}}"

    def query_belish(
            self,
            belish_query: str,
            limit: int | None = 10000,
            skip: int | None = 0,
            anno_key: str | None = None,
            anno_val: str | None = None,
    ):
        """Query the database with the given BQL query.

        Parameters
        ----------
        belish_query : str
            Valid BEL Query Language query
        limit : int | None
            Number of results to limit the output to. If None given, then returns all (may result in error).
        skip : int | None
            Number of results to skip. If None given, then skips none.
        anno_key : str | None
            Annotation key.
        anno_val : str | None
            Annotation value.
        """
        args = "/".join([belish_query, str(limit), str(skip), anno_key, anno_val])
        bq_decoded = requote_uri(args).replace("?", "%3F")
        req = self.url_template.format(bq=bq_decoded)
        resp = requests.get(req, auth=(self.user, self.__password))

        if resp.ok:
            results = resp.json(strict=False)["result"]
            self._data = results
            return results

        else:
            msg = {"error": "Problem parsing BEL statement, please check there are no special characters."}
            self._data = msg
            return msg

    def query_edges(self, superclass: str | None = None):
        """Generic query to ODB."""
        resp = requests.get(self.url_template.format(bq=superclass), auth=(self.user, self.__password))
        results = resp.json(strict=False)["result"]
        return results

    @property
    def data(self):
        """Return the stored results from the query as raw data."""
        if self._data:
            return [{k: v for k, v in x.items() if not k.startswith('@')} for x in self._data]

        else:
            raise ValueError("No results stored in object. Make a query first!")

    @property
    def table(self):
        """Return the stored results from the query as raw data."""
        if self._data:
            r = [{k: v for k, v in x.items() if not k.startswith('@')} for x in self._data]
            return pd.DataFrame(r)

        else:
            raise ValueError("No results stored in object. Make a query first!")


def _result_helper(object_names, row, unavailable_data='N/A') -> list:
    """
    Method that gets a list of column names (GraphDB results) and returns properly ordered values. Also applies
    a placeholder for values that where not retrieved.

    :return:
    """

    resulting_row = []

    for data_name in object_names:

        if data_name in row and row[data_name] == row[data_name] and row[data_name] is not None:
            data_value = row[data_name]

        else:
            data_value = unavailable_data

        if isinstance(data_value, list):  # Don't want lists printed to website
            data_value = "|".join(data_value)

        resulting_row.append(data_value)

    return resulting_row


def get_bel_data(belish, database: str = 'pharmacome', anno_key: str = "?", anno_val: str = "?") -> str:
    """Query the knowledge graph with a BELQL statement and return as JSON."""
    # Replace ? with %3F to paste in url
    belish = urllib.parse.quote(belish)
    api_client = ApiClient(database=database)
    raw_bel_data = api_client.query_belish(belish, anno_key=anno_key, anno_val=anno_val)

    belish_map = {
        'query': ['Subject', 'Relation', 'Object', 'PMID', 'Evidence', 'Publication', 'Journal', 'Last_Author',
                  'Publication_Date', "Annotation"],
        'table': [],
        'ref_list': [3],
        'ref_links': {
            3: 'https://www.ncbi.nlm.nih.gov/pubmed/',
        },
        'icon': None,
        'specific': {}
    }

    update_dict = {
        # Column names
        'column_names': belish_map['table'] if belish_map['table'] else belish_map['query'],

        # List of lists (rows)
        'data_rows': [],

        # Reference link definitions
        'ref_list': belish_map['ref_list'],
        'ref_links': belish_map['ref_links'],
        'link_icon': belish_map['icon'],
        'edge_specific': belish_map['specific'],
    }

    if "error" not in raw_bel_data:
        for row in raw_bel_data:
            update_dict['data_rows'].append(_result_helper(belish_map['query'], row))

    else:
        update_dict['data_rows'].append(raw_bel_data)
        update_dict['column_names'] = ["Error"]

    return json.dumps(update_dict)


def get_bel_edge_classes():
    """Gather all possible relation classes in the KG."""
    api_client = ApiClient(ssf="classes_by_abstract_parent", )
    raw_relations = api_client.query_edges('bel_relation')

    classes = []
    classes += _tree_strings(raw_relations[0])
    return {'bel_relation_class_list': classes}


def get_annotation_keys() -> dict:
    """Gather all annotation keys."""
    api_client = ApiClient(ssf="anno_keys", )
    results = api_client.query_edges()
    return {"anno_keys": sorted(results[0]["keys"])}


def get_annotation_values(anno_key: str):
    """Gather values for given annotation key."""
    if anno_key == "?" or not anno_key:
        return {"anno_vals": []}

    else:
        api_client = ApiClient(ssf="anno_vals", )
        results = api_client.query_edges(anno_key)
        return {"anno_vals": sorted(results[0]["vals"])}


def _tree_strings(tree_dict=None, tree_list=None, sub=0):
    """
    Helper function to build a tree structure view for a given dict or list
    :param tree_dict: Dictionary to build a tree from. Needs 'name','value','abstract' and 'children' parameters.
    :param tree_list: A list of tree elements that are on the same sub-level of the tree.
    :param sub: An int indicator to determine the sub-level of this run.
    :return: a list of dicts describing names and values to be used in an HTML dropdown select.
    """
    middle = "\u02EB"
    end = "\u02EA"

    if tree_dict is not None:
        tree_string_list = [{
            'name': f"{sub*' '}{tree_dict['name']}",
            'value': tree_dict['name']
        }] if sub == 0 else []

        clist = []
        cdict = {}
        for child in tree_dict['children']:
            clist.append(child['name'])

            if child['abstract']:
                cdict[child['name']] = _tree_strings(child, sub=sub+1)

        clist.sort()
        for c in clist:
            decorator = middle if c != clist[-1] else end
            space = (sub+1) * "\u2800"
            tree_string_list.append({
                'name': f"{space}{decorator} {c}",
                'value': c
            })

            if c in cdict:
                tree_string_list = tree_string_list + cdict[c]
    else:
        tree_string_list = []
        for element in tree_list:
            decorator = middle if element != tree_list[-1] else end
            space = (sub + 1) * "\u2800"
            tree_string_list.append({
                'name': f"{space}{decorator} {element}",
                'value': element
            })

    return tree_string_list
