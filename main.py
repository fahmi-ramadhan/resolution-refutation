"""
Main module for propositional logic resolution prover.
Handles command-line argument parsing and orchestrates the resolution process.
"""

import argparse
import sys

from colorama import Fore, Style
from parser import segment_sentence
from cnf_converter import to_cnf
from resolver import resolve


def parse_arguments():
    """
    Parses command-line arguments.
    
    Returns:
        tuple: (kb_file, query_file, verbose)
    """
    parser = argparse.ArgumentParser(
        description='Propositional Logic Resolution Prover',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py kb.txt query.txt       # Run resolution without verbose output
  python main.py kb.txt query.txt -v    # Run resolution with verbose output
  
File format:
  - Each line in the files should contain a propositional logic formula
  - Supported operators: ! (not), & (and), | (or), > (implies), = (if and only if)
  - Lines starting with # are treated as comments and ignored
  - The first line in the query file is used as the query
        """
    )
    parser.add_argument('kb_file', help='Path to the knowledge base file')
    parser.add_argument('query_file', help='Path to the query file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Print resolution steps')

    args = parser.parse_args()
    return args.kb_file, args.query_file, args.verbose


def read_from_file(filename):
    """
    Reads propositional sentences from a file.
    
    Args:
        filename (str): Path to the file containing propositional sentences
    
    Returns:
        list: List of propositional sentences
    
    Raises:
        FileNotFoundError: If the specified file is not found
        Exception: For any other errors while reading the file
    """
    sentences = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    sentences.append(line)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)

    return sentences


def main():
    """
    Main function to run the propositional logic resolution prover.
    
    Returns:
        int: 0 for successful execution, 1 for errors
    """
    kb_file, query_file, verbose = parse_arguments()

    kb_sentences = read_from_file(kb_file)
    query_sentences = read_from_file(query_file)

    if not query_sentences:
        print("Error: No query found in the query file.")
        return 1

    # Process the knowledge base
    knowledge_base = []
    for sentence in kb_sentences:
        sentence = to_cnf(segment_sentence(sentence))
        knowledge_base += sentence.copy()
        knowledge_base.append("&")

    # Process the query
    query = query_sentences[0]
    query = to_cnf(segment_sentence("!("+query+")"))
 
    # Do the resolution refutation procedure
    result = resolve(knowledge_base.copy() + query.copy(), verbose)
    if result:
        print(f"{Fore.GREEN}Knowledge base entails the query.{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}Knowledge base does not entail the query.{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
