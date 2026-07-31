import re

DEFAULT_ACRONYMS = (
    "scl-BR",
    "arg-AR",
    "bol-BO",
    "chl-CL",
    "cub-CU",
    "col-CO",
    "cri-CR",
    "ecu-EC",
    "esp-ES",
    "mex-MX",
    "per-PE",
    "prt-PR",
    "pry-PY",
    "psi-BR",
    "rve-BR",
    "rvt-BR",
    "spa-BR",
    "sss-BR",
    "sza-SZ",
    "ury-UY",
    "ven-VE",
    "wid-WI",
    "dom-DO",
)
CSV_FILES = (
    "documents_affiliations.csv",
    "documents_affiliation_nationality.csv",
    "documents_authors.csv",
    "documents_counts.csv",
    "documents_dates.csv",
    "documents_languages.csv",
    "documents_licenses.csv",
    "journals.csv",
    "journals_status_changes.csv",
)
KBART_TEMPLATE = "SciELO_{acronym}_AllTitles_{date}.csv"
ACRONYM_PATTERN = re.compile(r"^[a-z]{3}(?:-[A-Z]{2}|-)?$")
