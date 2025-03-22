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
        tuple: (kb_file, query_file, verbose, no_query)
    """
    parser = argparse.ArgumentParser(
        description='Propositional Logic Resolution Prover',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py kb.txt query.txt       # Run resolution without verbose output
  python main.py kb.txt query.txt -v    # Run resolution with verbose output
  python main.py kb.txt --no-query      # Run only knowledge base check without query
  
File format:
  - Each line in the files should contain a propositional logic formula
  - Supported operators: ! (not), & (and), | (or), > (implies), = (if and only if)
  - Lines starting with # are treated as comments and ignored
  - The first line in the query file is used as the query
        """
    )
    parser.add_argument('kb_file', help='Path to the knowledge base file')
    parser.add_argument('query_file', nargs='?', help='Path to the query file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Print resolution steps')
    parser.add_argument('--no-query', action='store_true',
                        help='Run only knowledge base check without query')
    
    args = parser.parse_args()
    
    # Check if --no-query is provided but query_file is also provided
    if args.no_query and args.query_file:
        parser.error("Cannot provide both query_file and --no-query")
    
    # Check if neither query_file nor --no-query is provided
    if not args.no_query and not args.query_file:
        parser.error("Either query_file or --no-query must be provided")
    
    return args.kb_file, args.query_file, args.verbose, args.no_query

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

def display_metrics(time_taken, peak_memory, stats):
    """
    Display performance metrics in a formatted way.
    
    Args:
        time_taken (float): Execution time in seconds
        peak_memory (float): Peak memory usage in MB
        stats (dict): Additional statistics about the resolution process
    """
    print(f"\n{Fore.CYAN}Performance metrics:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Execution time:{Style.RESET_ALL} {time_taken:.4f} seconds")
    print(f"  {Fore.YELLOW}Peak memory usage:{Style.RESET_ALL} {peak_memory:.2f} MB")
    
    print(f"\n{Fore.CYAN}Resolution statistics:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Initial clauses:{Style.RESET_ALL} {stats.get('initial_clauses', 0)}")
    print(f"  {Fore.YELLOW}Final clause count:{Style.RESET_ALL} {stats.get('final_clause_count', 0)}")
    print(f"  {Fore.YELLOW}Clause pairs examined:{Style.RESET_ALL} {stats.get('clause_pairs_examined', 0)}")
    
    # Calculate clauses per second if time is non-zero
    if time_taken > 0:
        clauses_per_second = stats.get('clauses_generated', 0) / time_taken
        print(f"  {Fore.YELLOW}Clauses per second:{Style.RESET_ALL} {clauses_per_second:.2f}")

def main():
    """
    Main function to run the propositional logic resolution prover.
    
    Returns:
        int: 0 for successful execution, 1 for errors
    """
    kb_file, query_file, verbose, no_query = parse_arguments()
    kb_sentences = read_from_file(kb_file)
    
    # Process the knowledge base
    knowledge_base = []
    for sentence in kb_sentences:
        sentence = to_cnf(segment_sentence(sentence))
        knowledge_base += sentence.copy()
        knowledge_base.append("&")
    
    if no_query:
        # Just check if the knowledge base is consistent (not self-contradictory)
        # To check consistency, we see if we can derive a contradiction
        if not knowledge_base:
            print(f"\n{Fore.GREEN}Knowledge base is satisfiable.{Style.RESET_ALL}")
            return 0
        
        knowledge_base.pop()  # Remove the last "&"
        result, time_taken, peak_memory, stats = resolve(knowledge_base.copy(), verbose)
        
        display_metrics(time_taken, peak_memory, stats)
        
        if not result:
            print(f"\n{Fore.GREEN}Knowledge base is satisfiable.{Style.RESET_ALL}")
            return 0
        else:
            print(f"\n{Fore.RED}Knowledge base is not satisfiable (self-contradictory).{Style.RESET_ALL}")
            return 1
    else:
        # Normal mode with a query
        query_sentences = read_from_file(query_file)
        if not query_sentences:
            print("Error: No query found in the query file.")
            return 1
            
        # Process the query
        query = query_sentences[0]
        query = to_cnf(segment_sentence("!("+query+")"))
    
        # Do the resolution refutation procedure
        result, time_taken, peak_memory, stats = resolve(knowledge_base.copy() + query.copy(), verbose)
        
        display_metrics(time_taken, peak_memory, stats)
        
        if result:
            print(f"\n{Fore.GREEN}Knowledge base entails the query.{Style.RESET_ALL}")
            return 0
        else:
            print(f"\n{Fore.RED}Knowledge base does not entail the query.{Style.RESET_ALL}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
