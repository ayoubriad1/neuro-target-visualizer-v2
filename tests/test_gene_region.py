from atlas_regions import ATLAS_REGIONS
from gene_region import get_gene_citation, known_genes, suggest_regions


def test_suggest_regions_known_gene():
    regions = suggest_regions("DRD2")
    assert regions is not None
    assert "Striatum (Caudate)" in regions


def test_suggest_regions_case_insensitive_and_aliases():
    assert suggest_regions("drd2") == suggest_regions("D2") == suggest_regions("DRD2")


def test_suggest_regions_unknown_gene_returns_none():
    assert suggest_regions("NotARealGene") is None


def test_get_gene_citation_known_gene():
    assert get_gene_citation("DRD2") is not None


def test_get_gene_citation_unknown_gene_returns_none():
    assert get_gene_citation("NotARealGene") is None


def test_every_known_gene_has_regions_and_citation():
    for gene in known_genes():
        regions = suggest_regions(gene)
        assert regions, f"{gene} has no suggested regions"
        assert get_gene_citation(gene), f"{gene} has no citation"


def test_every_suggested_region_is_a_real_atlas_region():
    # Guards against a typo in gene_region.py's region names silently
    # suggesting a region that doesn't actually exist in this app's atlas.
    for gene in known_genes():
        for region in suggest_regions(gene):
            assert region in ATLAS_REGIONS, f"{region} (from {gene}) not in ATLAS_REGIONS"
