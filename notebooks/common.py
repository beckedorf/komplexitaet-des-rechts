from bs4 import BeautifulSoup 
import networkx as nx
import pandas as pd
import numpy as np
from IPython.display import display
from svglib.svglib import svg2rlg
import altair as alt
import subprocess
import os
import json
import re
import locale
from altair_saver import save
from collections import defaultdict, Counter
import random
import itertools
import subprocess
from quantlaw.utils.networkx import *

from altair.vega.v5.display import Vega as VegaV5

locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')

data_figures_path = '../data_figures'
data_pickles_path = '../data_pickles'


# Add chromedriver path (needed to save altair plots)
import os
os.environ["PATH"] += os.pathsep + r'/usr/local/bin'

# Custom theme

std_font =  "Times New Roman"

def cmuserif():
    cmu_label_title = {
        "labelFont": std_font,
        "titleFont": std_font,
        "titleFontWeight": "bold",
#        "labelFontSize": 16,
#        "titleFontSize": 16,
    }
    return {
        "config" : {
             "title": {
                 'font': std_font,
                 "fontWeight": "bold"

             },
            "axis": cmu_label_title,
            "legend": cmu_label_title,
            "headerColumn": cmu_label_title,
            "headerRow": cmu_label_title,
            "headerFacet": cmu_label_title,
            "text": {
                  "font": std_font,
            },
            "view": {
                'width':400,
                'height':160,
            },
            "line": {
              "size": 1,  
            },
            "point": {
                "size": 50,
            },
            "locale": {
                "number": {
                  "decimal": ",",
                  "thousands": ".",
                  "grouping": [3],
                  "currency": ["", " €"]
                },
                "time": {
                  "dateTime": "%A, der %e. %B %Y, %X",
                  "date": "%d.%m.%Y",
                  "time": "%H:%M:%S",
                  "periods": ["AM", "PM"],
                  "days": ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
                  "shortDays": ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
                  "months": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
                  "shortMonths": [ "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
                }
            }
        }
    }
# register the custom theme under a chosen name
alt.themes.register('cmuserif', cmuserif)
# enable the newly registered theme
alt.themes.enable('cmuserif')


# save drawing

diss_data_path = '../beckedorf-diss-data.json'
diss_used_abks_path = '../beckedorf-used-abks.json'

def save_chart(chart, filename, used_abks=None):
    if type(chart) is VegaV5:
        vega_data = chart.spec
    else:
        vega_data = chart
    os.makedirs(data_figures_path, exist_ok=True)
    save(vega_data, f'{data_figures_path}/{filename}.pdf', vega_cli_options=['-f', 'de-DE.json'], method='node',)
    
    if used_abks:
        save_used_abks(filename, used_abks)
        
    return chart

def save_chart_and_crop(chart, filename, used_abks=None):
    r = save_chart(chart, filename, used_abks)
    savepath = f'{data_figures_path}/{filename}.pdf'
    subprocess.run(["pdfcrop", savepath, savepath], check=True)
    return r
    

def save_used_abks(filename, used_abks):
    if os.path.exists(diss_used_abks_path):
        with open(diss_used_abks_path) as f:
            abks = json.load(f)
    else:
        abks = dict()
    abks[filename] = list(used_abks)
    with open(diss_used_abks_path, 'w') as f:
        json.dump(abks, f, indent=4, ensure_ascii=False)
    
def diss_data(key, value):
    str_value = str(value)
    if os.path.exists(diss_data_path):
        with open(diss_data_path) as f:
            data = json.load(f)
        data[key] = str_value
    else:
        data = {key: str_value}
    with open(diss_data_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(key, '-', str_value)
    
def get_diss_data(key):
    with open(diss_data_path) as f:
        data = json.load(f)
    return data[key]
    
def format_list(values, join_std=', das ', join_last=' und das '):
    result = values.copy()
    result[-2:] = [join_last.join(result[-2:])]
    result = join_std.join(result)
    return result

def format_mio(value):
    return de_num_format(f'{value/10**6:.2f}') + ' Mio.'

def de_num_format(value):
    return value.replace(",", "X").replace(".", ",").replace("X", ".")

def abs_to_rel(abs_array):
    rel_array = abs_array / abs_array[0]
    return rel_array

def binned_df(values, bins: np.arange, year):
    df = pd.DataFrame(values, columns=['x'])
    binned = df.groupby(pd.cut(df.x, bins=bins)).count()
    binned['bin_min'] = bins[:-1]
    binned['bin_max'] = bins[1:]
    binned = binned.reset_index(drop=True)
    binned['Jahr'] = year
    return binned

def get_docparts_with_p(soup):
    return [
        soup.titelzeile,
        soup.leitsatz,
        soup.sonstosatz,
        soup.tenor,
        soup.tatbestand,
        soup.entscheidungsgruende,
        soup.gruende,
        soup.sonstlt,
        soup.abwmeinung
    ]

def get_node_count_for_type(G, node_types):
    return len([n for n, t in G.nodes(data='type') if t in node_types and G.nodes[n]['chars_n'] > 0])


def quotient_decision_graph(G, merge_decisions, merge_statutes):
    H = nx.DiGraph()

    # Decision nodes and containment edges
    if merge_decisions:
        documents = [n for n, b in G.nodes(data='type') if b == 'document']
        H.add_nodes_from([(n.split('_')[0], G.nodes[n]) for n in documents])
    else:
        decisions = [n for n, b in G.nodes(data='bipartite') if b == 'decision']
        H.add_nodes_from([(n, G.nodes[n]) for n in decisions])

        containment = [(u, v, d) for u, v, d in G.edges(data=True) if d['edge_type'] == 'containment']
        H.add_edges_from(containment)

    # Statute nodes
    if merge_statutes:
        statute_nodes = [n for n, b in G.nodes(data='bipartite') if b == 'statute']
        statute_nodes_merged = list(sorted({
            n.split('_')[0] for n in statute_nodes
        }))
        H.add_nodes_from(statute_nodes_merged, bipartite='statute')
    else:
        statute_nodes = [n for n, b in G.nodes(data='bipartite') if b == 'statute']
        H.add_nodes_from([(n, G.nodes[n]) for n in statute_nodes])

    # Reference edges
    references = [[u, v, d] for u, v, d in G.edges(data=True) if d['edge_type'] == 'reference']

    references_dict = defaultdict(int)
    for u, v, d in references:
        u_converted = u.split('_')[0] if merge_decisions else u
        v_converted = v.split('_')[0] if merge_statutes else v
        references_dict[(u_converted, v_converted)] += d['weight']
        
    references_converted = [
        (k[0], k[1], {'weight': v, 'edge_type': 'reference'})
        for k, v in references_dict.items()
     ]
    H.add_edges_from(references_converted)

    return H

def jitter(data):
    random.seed(data.sum())
    return pd.Series([v + random.random() - .5 for v in data])

def large_labels(chart):
    axis = dict(titleFontSize=15, labelFontSize=14)
    return chart.configure_headerColumn(**axis)

def truncate(text, max_length):
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'

def graph_to_vega_data(D, dataset, min_size=None, rollup_up=0, truncate_len=20, roll_down=0, size_attr='weight'):
    data = [{'id':'root', 'size': D.nodes['root'][size_attr]}]
    for parent_node, node in nx.bfs_tree(D, 'root', depth_limit=None).edges:
        if 'abks' in D.nodes[node]:
            name = ','.join(D.nodes[node]['abks'])
        elif D.out_degree(node):
            name = None
        elif dataset.lower() == 'us':
            name = node.split('_')[0][:-1] + '/' + D.nodes[node]['heading'].replace('CHAPTER ', '').split('-')[0]
        elif dataset.lower() == 'de_decision':
            name = node
        elif type(node) is str and node.endswith('_000001'):
            name = node.split('_')[1]
        elif 'heading' in D.nodes[node]:
            name = node.split('_')[1] + ', ' + ' '.join(D.nodes[node]['heading'].split(' ')[:2])
        else:
            name = node.split('_')[1]
        
        
        if roll_down and len(nx.ancestors(D, node)) > roll_down:
            continue
        
        data.append({
            'id': str(node),
            'parent': str(parent_node),
            'size': D.nodes[node][size_attr],
            'name': truncate(name, truncate_len)

        })
    
    if min_size:
        data = [d for d in data if d.get('size') > min_size]
    for _ in range(rollup_up):
        parents = {d['parent'] for d in data if 'parent' in d}
        data = [d for d in data if d['id'] in parents]

    return data

def clustering_to_community_abk_latex(clustering, count_filter=lambda cnt: cnt>= 9000):
    abks = defaultdict(Counter)

    for node, community in nx.get_node_attributes(clustering.graph, 'community').items():
        if type(node) is str and node.endswith('_000001'):
            abk = node.split('_')[1]
        elif 'heading' in clustering.graph.nodes[node]:
            abk = node.split('_')[1] + ' (' + ' '.join(clustering.graph.nodes[node]['heading'].split(' ')[:2]) + ')'
        else:
            abk = node.split('_')[1]
        abks[community][abk] += clustering.graph.nodes[node]['tokens_n']

    abks = {k: v for k, v in abks.items() if len(v) > 1}
    community_keys_sorted = sorted(abks.keys(), key=lambda k: sum(abks[k].values()), reverse=True)

    latex = '''\\begin{tabular}{cp{.85\\textwidth}}
    \\textbf{Nr.} & \\textbf{Abkürzungen (sortiert nach Gesetzeslänge in Token)} \\\\ \\hline
'''

    for idx, community in enumerate(community_keys_sorted):
        idx = community # Uncomment to use real numbers
        com_abks = abks[community]
        filtered_abks = [abk for abk, count in com_abks.most_common() if count_filter(count)]
        if len(filtered_abks) > 1:
            latex += f'{idx+1} & '
            latex += ', '.join(filtered_abks)

            latex += ' \\\\ \\hline\n'

    latex = latex[:-len(' \\hline\n')]
    latex += '''
    \end{tabular}
    '''
    return latex

def make_weighted(mG):
    if nx.is_directed(mG):
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    G.add_nodes_from(mG.nodes(data=True))
    weight_by_edge_type = defaultdict(lambda: defaultdict(float))
    for u,v,data in mG.edges(data=True):
        w = data['weight'] if 'weight' in data else 1.0
        if G.has_edge(u,v):
            G[u][v]['weight'] += w
        else:
            G.add_edge(u, v, weight=w)
        edge = (u, v)
        edge_type = data['edge_type']
        weight_by_edge_type[edge_type][edge] += w
    
    for edge_type, weights in weight_by_edge_type.items():
        nx.set_edge_attributes(G, weights, f'weight_{edge_type}')
    
    return G

def propagate_attrs_to_descendents(G, attrs=['gericht']):
    for attr in attrs:
        doknr_gericht = {
            n.split('_')[0]: d[attr] 
            for n, d in G.nodes(data=True) 
            if n != 'root' and d['bipartite'] == 'decision' and d['type'] == 'document'
        }
        gericht_attrs = {
            n: doknr_gericht[n.split('_')[0]] 
            for n, b in G.nodes(data='bipartite') 
            if n != 'root' and b == 'decision'
        }
        nx.set_node_attributes(G, gericht_attrs, attr)


alle_gericht_scale_range = [
    'rgb(0, 0, 0)',
    'rgb(76, 120, 168)',
    'rgb(245, 133, 24)',
    'rgb(228, 87, 86)',
    'rgb(114, 183, 178)',
    'rgb(84, 162, 75)',
    'rgb(238, 202, 59)',
    'rgb(178, 121, 162)',
    'rgb(255, 157, 166)',
]

alle_gericht_ohne_bpatg_scale_range = alle_gericht_scale_range[:4] + alle_gericht_scale_range[5:]
alle_gericht_ohne_bpatg_scale_range


def list_dir(path, type):
    return [f for f in os.listdir(path) if f.endswith(type)]


def select_citekey(data, abk_units):
    for citekey, cnt in data:
        abk, nr = citekey.split('_')
        try:
            unit = abk_units[abk]
        except KeyError:
            print(abk, 'not in abk_units')
            unit = '§'
        yield (
            f'{unit} {nr} {abk}',
            cnt,
        )
        
def select_human_readable_citekey(data, G):
    return [
        (
            ' '.join(G.nodes[n]['heading'].split(' ')[:2]) + ' ' + G.nodes[n]['citekey'].split('_')[0],
            cnt
        )
        for n, cnt in data
    ]

def select_key_parts(data, pos):
    return [
        (
            n.split('_')[pos],
            cnt,
        )
        for n, cnt in data
    ]

def make_occurrence_graph(G, decision_level='seqitem', decision_to_edge_attrs=['gericht', 'spruchkoerper', 'datum']):
    H = nx.MultiGraph()
    H.add_nodes_from([(n, d) for n, d in G.nodes(data=True) if d['bipartite'] == 'statute'])
    edges = list()
    for n, d in G.nodes(data=True):
        if d['bipartite'] == 'decision' and d.get('type') == decision_level:
            targets = sorted([v for u, v in G.edges(n)])
            decision_edges = [
                (
                    u,
                    v,
                    {
                        k: d[k]
                        for k in decision_to_edge_attrs
                    }
                )
                for u, v in itertools.combinations(targets, 2)
            ]
            edges += decision_edges
    H.add_edges_from(edges, edge_type='cooccurrence')
    return H


def filter_edges(G, edge_attr, edge_val_to_remove):
    """
    Create a new graph with all nodes in G and edges of type 'edge_type_to_remove' removed.
    """
    nG = type(G)()  # construct graph of same type as G
    nG.add_nodes_from(G.nodes(data=True))
    nG.add_edges_from(
        [x for x in G.edges(data=True) if x[-1].get(edge_attr) != edge_val_to_remove]
    )
    return nG
