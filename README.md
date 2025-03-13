# PubMed Papers

A Python command-line tool to fetch research papers from PubMed based on a user-specified query, identify papers with at least one author affiliated with a pharmaceutical or biotech company, and return the results as a CSV file.

## Features

- Fetch papers using the PubMed API with support for PubMed's full query syntax
- Filter papers to identify those with authors from pharmaceutical or biotech companies
- Export results as CSV with details including publication information and company affiliations
- Command-line interface with options for debugging and output file specification

## Code Organization

The project is organized as follows:

```
pubmed_papers/
├── pyproject.toml          # Poetry configuration and package metadata
├── README.md               # This documentation file
├── pubmed_papers/          # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── fetcher.py          # PubMed API interaction
│   ├── parser.py           # Data parsing and export
│   └── utils.py            # Utility functions
└── tests/                  # Test directory
    ├── __init__.py
    ├── test_fetcher.py
    ├── test_parser.py
    └── test_utils.py
```

### Architecture

The code is structured into distinct modules:

1. **fetcher.py**: Contains the `PubMedFetcher` class that interacts with the PubMed API using the Biopython's Entrez module. It handles searching for papers, fetching details, and extracting relevant information.

2. **parser.py**: Contains the `PaperDataParser` class that processes the fetched data, filters papers with company authors, and exports the results to CSV.

3. **utils.py**: Contains utility functions for logging, validation, and keyword lists for identifying academic vs. company affiliations.

4. **cli.py**: Implements the command-line interface, argument parsing, and serves as the main entry point for the application. It orchestrates the workflow by calling the appropriate functions from the other modules.

## Installation

This project uses Poetry for dependency management and packaging.

1. First, ensure you have [Poetry installed](https://python-poetry.org/docs/#installation).

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pubmed-papers.git
   cd pubmed-papers
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

After installation, you can use the `get-papers-list` command to query PubMed:

```bash
# Basic usage
poetry run get-papers-list "cancer therapy"

# Save results to a CSV file
poetry run get-papers-list "diabetes treatment" -f results.csv

# Enable debug mode
poetry run get-papers-list "covid vaccine" -d

# Specify maximum number of results
poetry run get-papers-list "alzheimer's disease" -m 100

# Provide your email for NCBI API (recommended)
poetry run get-papers-list "gene therapy" -e your.email@example.com
```

### Command-line Options

- `query`: PubMed search query (supports full PubMed query syntax)
- `-f, --file`: Output file path to save results as CSV
- `-d, --debug`: Print debug information during execution
- `-m, --max-results`: Maximum number of papers to fetch (default: 500)
- `-e, --email`: Email address for NCBI Entrez API
- `-k, --api-key`: NCBI API key to increase rate limits
- `-h, --help`: Show help message

## How It Works

1. The program takes a PubMed search query from the user
2. It searches PubMed for matching papers using the Entrez API
3. For each paper, it retrieves detailed information including author affiliations
4. It identifies papers with at least one author affiliated with a pharmaceutical or biotech company
5. Results are either saved to a CSV file or displayed in the console

### Identifying Non-academic Authors

The program uses heuristics to identify non-academic affiliations:

1. It checks author affiliations for keywords indicating company affiliations (e.g., "pharma", "biotech", "inc", "corp")
2. It filters out academic institutions based on keywords (e.g., "university", "college", "hospital")
3. It attempts to extract company names and corresponding author emails when available

## Development

### Running Tests

```bash
poetry run pytest
```

### Type Checking

```bash
poetry run mypy pubmed_papers
```

## Tools Used

- [Poetry](https://python-poetry.org/) - Dependency management and packaging
- [Biopython](https://biopython.org/) - Entrez API access for PubMed queries
- [Pandas](https://pandas.pydata.org/) - Data manipulation and CSV export
- [Requests](https://requests.readthedocs.io/) - HTTP requests
- [PyTest](https://pytest.org/) - Testing framework
- [MyPy](https://mypy.readthedocs.io/) - Static type checking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [NCBI PubMed](https://pubmed.ncbi.nlm.nih.gov/) for providing the API
- [Entrez Programming Utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) documentation 
  
## Bonus Features

### Modular Structure

The project is split into two main parts:
1. A library (`pubmed_papers`) that can be imported and used in other Python projects
2. A command-line interface (`get-papers-list`) that uses the library

This separation allows for greater flexibility and reusability. You can import the library in your own code:

```python
from pubmed_papers import PubMedFetcher, PaperDataParser

# Initialize the fetcher
fetcher = PubMedFetcher(email="your.email@example.com")

# Search for papers
papers = fetcher.search("alzheimer's disease")

# Fetch details
details = fetcher.fetch_details(papers)

# Filter and process results
filtered = PaperDataParser.filter_papers_with_company_authors(details)
```

### Test PyPI Publishing

The package is also configured for publishing to Test PyPI. To publish:

1. Update version in `pyproject.toml`

2. Build the package:
   ```bash
   poetry build
   ```

3. Publish to Test PyPI:
   ```bash
   poetry config repositories.testpypi https://test.pypi.org/legacy/
   poetry publish --repository testpypi
   ```

4. Install from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ pubmed-papers
   ```

## Acknowledgments

- [NCBI PubMed](https://pubmed.ncbi.nlm.nih.gov/) for providing the API
- [Entrez Programming Utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) documentation
