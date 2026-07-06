"""Best-effort RCSB PDB metadata lookup (data.rcsb.org REST API) - resolves a
PDB ID to its gene symbol, UniProt accession and entry title, so a bulk
docking-results sheet that only lists a PDB_ID column can still get "which
target is this" filled in automatically instead of the user typing it by
hand.

Checked directly against the live API before writing this module: a PDB
entry's metadata is structural/genetic only. There is no anatomical,
tissue, or brain-region field anywhere in it - fetch_pdb_metadata()
deliberately stops at gene identity. Turning a gene into a candidate brain
region is a separate, hand-curated step (see gene_region.py); it is not,
and cannot be, sourced from RCSB.

Network errors, unknown IDs, or unrecognized response shapes all return
None rather than raising - a bad/typo'd PDB ID in one row of a bulk import
must never crash the whole lookup.
"""
from dataclasses import dataclass

import requests
import streamlit as st

_API_URL = "https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
_TIMEOUT_S = 6


@dataclass(frozen=True)
class PDBMetadata:
    pdb_id: str
    gene: str | None
    uniprot_id: str | None
    title: str | None
    organism: str | None


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_pdb_metadata(pdb_id: str) -> PDBMetadata | None:
    """Looks up entity 1 of `pdb_id` (the first polymer entity - the typical
    receptor/target chain for a single-target crystal structure; complexes
    with multiple distinct chains may need a different entity number, not
    handled here). Returns None on any network error, HTTP error, unparsable
    response, or an entry with no gene/UniProt/title info at all - cached
    for 24h so a repeated lookup of the same ID doesn't re-hit the network.
    """
    pdb_id = pdb_id.strip().upper()
    if not pdb_id:
        return None
    try:
        resp = requests.get(_API_URL.format(pdb_id=pdb_id), timeout=_TIMEOUT_S)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None
    if not isinstance(data, dict):
        return None

    gene = None
    for src in data.get("entity_src_gen") or []:
        raw_gene = src.get("pdbx_gene_src_gene")
        if raw_gene:
            gene = raw_gene[0] if isinstance(raw_gene, list) else raw_gene
            break

    uniprot_id = None
    for align in data.get("rcsb_polymer_entity_align") or []:
        if align.get("reference_database_name") == "UniProt":
            uniprot_id = align.get("reference_database_accession")
            break

    organism = None
    orgs = data.get("rcsb_entity_source_organism") or []
    if orgs:
        organism = orgs[0].get("ncbi_scientific_name")

    title = (data.get("rcsb_polymer_entity") or {}).get("pdbx_description")

    if gene is None and uniprot_id is None and title is None:
        return None
    return PDBMetadata(pdb_id=pdb_id, gene=gene, uniprot_id=uniprot_id, title=title, organism=organism)
