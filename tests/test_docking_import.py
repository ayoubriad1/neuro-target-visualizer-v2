from docking_import import parse_csv, parse_vina_score


def test_parse_csv_basic_named_regions():
    text = "region,kcal\nThalamus,-9.2\nHippocampus,-6.5\n"
    result = parse_csv(text)
    assert result.errors == []
    assert len(result.rows) == 2
    assert result.rows[0].name == "Thalamus"
    assert result.rows[0].kcal == -9.2
    assert result.rows[0].coordinates is None
    assert result.rows[1].name == "Hippocampus"


def test_parse_csv_case_insensitive_header_aliases():
    text = "Region,Affinity\nThalamus,-7.0\n"
    result = parse_csv(text)
    assert result.errors == []
    assert result.rows[0].kcal == -7.0


def test_parse_csv_kcal_mol_header_alias():
    text = "name,kcal_mol\nThalamus,-8.1\n"
    result = parse_csv(text)
    assert result.errors == []
    assert result.rows[0].name == "Thalamus"


def test_parse_csv_exact_coordinates():
    text = "region,kcal,x,y,z\n,-9.0,10,-20,5\n"
    result = parse_csv(text)
    assert result.errors == []
    assert result.rows[0].coordinates == (10.0, -20.0, 5.0)
    assert result.rows[0].name == "Custom (10, -20, 5)"


def test_parse_csv_exact_coordinates_with_custom_label():
    text = "region,kcal,x,y,z\nDBS target A,-9.0,10,-20,5\n"
    result = parse_csv(text)
    assert result.errors == []
    assert result.rows[0].name == "DBS target A"
    assert result.rows[0].coordinates == (10.0, -20.0, 5.0)


def test_parse_csv_rejects_unknown_region_name():
    text = "region,kcal\nNotARealRegion,-7.0\n"
    result = parse_csv(text)
    assert result.rows == []
    assert len(result.errors) == 1
    assert "unknown region" in result.errors[0]


def test_parse_csv_rejects_positive_affinity():
    text = "region,kcal\nThalamus,7.0\n"
    result = parse_csv(text)
    assert result.rows == []
    assert "must be negative" in result.errors[0]


def test_parse_csv_rejects_unparseable_affinity():
    text = "region,kcal\nThalamus,not-a-number\n"
    result = parse_csv(text)
    assert result.rows == []
    assert "could not parse affinity" in result.errors[0]


def test_parse_csv_missing_affinity_column():
    text = "region,score\nThalamus,-7.0\n"
    result = parse_csv(text)
    assert result.rows == []
    assert "No affinity column" in result.errors[0]


def test_parse_csv_empty_file():
    result = parse_csv("")
    assert result.rows == []
    assert "Empty file" in result.errors[0]


def test_parse_csv_partial_success_reports_both_good_and_bad_rows():
    text = "region,kcal\nThalamus,-9.0\nBadRegion,-3.0\nHippocampus,5.0\n"
    result = parse_csv(text)
    assert len(result.rows) == 1
    assert result.rows[0].name == "Thalamus"
    assert len(result.errors) == 2


def test_parse_csv_carries_pdb_protein_ligand_metadata():
    text = "pdb_id,protein,ligand,region,kcal\n6CM4,DRD2,Compound_A,Striatum (Caudate),-9.1\n"
    result = parse_csv(text)
    assert result.errors == []
    row = result.rows[0]
    assert row.pdb_id == "6CM4"
    assert row.protein == "DRD2"
    assert row.ligand == "Compound_A"


def test_parse_csv_metadata_columns_are_optional():
    text = "region,kcal\nThalamus,-9.2\n"
    result = parse_csv(text)
    assert result.errors == []
    row = result.rows[0]
    assert row.pdb_id is None
    assert row.protein is None
    assert row.ligand is None


def test_parse_csv_gene_column_alias():
    text = "gene,region,kcal\nDRD2,Striatum (Caudate),-9.1\n"
    result = parse_csv(text)
    assert result.errors == []
    assert result.rows[0].protein == "DRD2"


def test_parse_csv_missing_region_suggests_candidates_for_known_gene():
    text = "protein,kcal\nDRD2,-9.1\n"
    result = parse_csv(text)
    assert result.rows == []
    assert "typically associated with" in result.errors[0]
    assert "Striatum (Caudate)" in result.errors[0]


def test_parse_csv_missing_region_no_suggestion_for_unknown_gene():
    text = "protein,kcal\nNotARealGene,-9.1\n"
    result = parse_csv(text)
    assert result.rows == []
    assert "isn't in this app's gene/receptor lookup table" in result.errors[0]


def test_parse_csv_missing_region_no_protein_column_unchanged_message():
    text = "region,kcal\n,-9.1\n"
    result = parse_csv(text)
    assert result.rows == []
    assert result.errors[0] == "Line 2: missing region name (and no x/y/z given)."


def test_parse_vina_score_from_pdbqt_remark():
    text = "MODEL 1\nREMARK VINA RESULT:    -8.3      0.000      0.000\nATOM ...\n"
    assert parse_vina_score(text) == -8.3


def test_parse_vina_score_from_pdbqt_takes_first_best_pose():
    text = (
        "REMARK VINA RESULT:    -8.3      0.000      0.000\n"
        "REMARK VINA RESULT:    -7.9      1.200      2.400\n"
    )
    assert parse_vina_score(text) == -8.3


def test_parse_vina_score_from_log_table():
    text = """
-----+------------+----------+----------
   1       -8.3      0.000      0.000
   2       -7.9      1.203      2.431
"""
    assert parse_vina_score(text) == -8.3


def test_parse_vina_score_unrecognized_format_returns_none():
    assert parse_vina_score("this is not a vina file at all") is None
