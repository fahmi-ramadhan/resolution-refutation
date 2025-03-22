# resolution-refutation

## Overview

This project implements a propositional logic resolution prover. It includes modules for parsing propositional logic formulas, converting them to Conjunctive Normal Form (CNF), and resolving them using the resolution principle.

## Project Structure

- `main.py`: The main module that handles command-line argument parsing and orchestrates the resolution process.
- `parser.py`: Contains functions for tokenizing and parsing propositional logic formulas.
- `cnf_converter.py`: Converts propositional logic formulas to Conjunctive Normal Form (CNF).
- `resolver.py`: Implements the resolution-based theorem proving for propositional logic.
- `test.py`: Contains unit tests for the parser, CNF converter, and resolver modules.
- `datasets/`: Contains knowledge base and query files.
- `loading_indicator.py`: A simple loading indicator for the command-line interface.

## Usage

### Command-Line Interface

To run the resolution prover, use the following command:

```sh
# Run with knowledge base and query files
python main.py <kb_file> <query_file> [-v]

# Run only with knowledge base to check for consistency
python main.py <kb_file> --no-query [-v]
```

For detailed usage information, examples, and file format specifications, run:

```sh
python main.py -h
```
