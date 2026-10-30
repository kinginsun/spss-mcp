from spss_mcp.output_parser import extract_errors, parse_spss_output


def test_extract_errors_requires_hash():
    real = ">Error # 61 in column 10.  Text: foo.sav\n>The filename is not valid.\n"
    errs = extract_errors(real)
    assert len(errs) == 1
    assert errs[0].startswith("Error #61")
    # ANOVA residual rows must not match (no '#').
    assert extract_errors("Error      15085.394                 59   255.685\n") == []


def test_anova_error_ss_column_is_not_an_spss_error():
    # GLM within-subjects tables label the residual row "Error" followed by SS.
    table = (
        "Tests of Within-Subjects Effects\n"
        "Source     Type III Sum of Squares   df   Mean Square\n"
        "wave       1234.5                    2    617.25\n"
        "Error      15085.394                 59   255.685\n"
    )
    assert extract_errors(table) == []
    md = parse_spss_output(table)
    assert "### Errors" not in md
