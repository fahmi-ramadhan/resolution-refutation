"""
Resolution module for propositional logic resolution prover.
Implements resolution refutation procedure for propositional logic formulas.
"""

import colorama
from colorama import Fore, Style
from parser import forward_slice
from loading_indicator import LoadingIndicator
import time
import psutil
import os

colorama.init(autoreset=True)

def clause_to_frozenset(sentence):
    """
    Creates a frozenset from list of operators and literals in a clause.
    
    Args:
        sentence (list): Propositional formula in CNF
    
    Returns:
        frozenset: immutable set of literals in the clause
    
    Note:
        The sentence should be in CNF and of the form ['(', 'A', '|', 'B', '|',...,'|', 'Z', ')']
        where literals like A, B, ..., Z can be negated.

    Example:
        ['(', 'A', '|', '!B', ')'] -> frozenset({'A', '!B'})
    """
    m = set()
    j = 1 if sentence[0] == "(" else 0
    L = len(sentence) - 1 if sentence[0] == "(" else len(sentence)
    while j < L:
        literal, j = forward_slice(sentence, j)
        if literal[0] == "!":
            m.add("!" + str(literal[1]))
        else:
            m.add(str(literal[0]))
        # [NOTE] 'j' is incremented by 2 to escape '|' and reach next literal.
        j += 2
    return frozenset(m)


def format_clause(clause):
    """
    Formats a clause for display.
    
    Args:
        clause (frozenset): Clause to format
    
    Returns:
        str: Formatted string representation of the clause
    """
    return "[" + ", ".join(sorted(clause)) + "]"


def resolve_clause_pair(clause1, clause2):
    """
    Resolves two clauses and returns a set of resulting resolvents along with the eliminated literals.
    
    Args:
        clause1 (frozenset): First clause
        clause2 (frozenset): Second clause
    
    Returns:
        list: List of tuples (resolvent_clause, eliminated_pair) where eliminated_pair is a string
              representing the complementary literals that were eliminated
    """
    resolvents = []

    for literal in clause1:
        # Compute the negation of the literal
        neg_literal = literal[1:] if literal.startswith("!") else "!" + literal
        
        if neg_literal in clause2:
            # Create new clause by removing the complementary literals and combining the rest
            new_clause = frozenset(clause1.difference({literal}).union(clause2.difference({neg_literal})))
            # Track which complementary literals were eliminated
            eliminated_pair = f"{literal}/{neg_literal}"
            resolvents.append((new_clause, eliminated_pair))

    return resolvents


def get_memory_usage():
    """
    Get current memory usage of the process.
    
    Returns:
        float: Memory usage in MB
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Convert to MB
    return memory_info.rss / (1024 * 1024)


def resolve(sentence, mode):
    """
    Resolves the given sentence using the resolution principle.
    
    Args:
        sentence (list): Propositional formula in CNF
        mode (bool): Whether to print resolution steps
    
    Returns:
        tuple: (result, time_taken, peak_memory, stats)
            - result (bool): True if the KB entails the query, False otherwise
            - time_taken (float): Time taken for resolution in seconds
            - peak_memory (float): Peak memory usage during resolution in MB
            - stats (dict): Additional statistics about the resolution process
    """
    start_time = time.time()
    initial_memory = get_memory_usage()
    peak_memory = initial_memory
    
    # Initialize loading indicator if not in verbose mode
    loading = None
    if not mode:
        loading = LoadingIndicator("Performing resolution")
        loading.start()
    
    # Statistics tracking
    stats = {
        "steps": 0,
        "clauses_generated": 0,
        "clause_pairs_examined": 0
    }
    
    # Convert to clause format
    clause = []
    # clause_set is a set of frozensets, where each frozenset represent a clause
    clause_set = set()

    # Process the sentence into clauses in frozenset form
    for literal in sentence:
        if literal == "&":
            clause_set.add(clause_to_frozenset(clause))
            clause.clear()
        else:
            clause.append(literal)

    # Add the last clause
    clause_set.add(clause_to_frozenset(clause))

    if mode:
        print(f"{Fore.CYAN}KB ∪ ¬Q:{Style.RESET_ALL}")
        formatted_clauses = [f"{Fore.MAGENTA}[{', '.join(clause)}]{Style.RESET_ALL}" for clause in clause_set]
        print(f"  {{{', '.join(formatted_clauses)}}}")
        print(f"\n{Fore.CYAN}Resolution steps:{Style.RESET_ALL}")


    stats["initial_clauses"] = len(clause_set)
    step_counter = 0
    prev_length = 0

    while prev_length != len(clause_set):
        prev_length = len(clause_set)
        new_resolvents = set()
        
        # Check current memory usage
        current_memory = get_memory_usage()
        peak_memory = max(peak_memory, current_memory)
        
        clause_list = list(clause_set)
        for i in range(len(clause_list)):
            for j in range(i+1, len(clause_list)):
                c1, c2 = clause_list[i], clause_list[j]
                stats["clause_pairs_examined"] += 1
                resolvent_pairs = resolve_clause_pair(c1, c2)
                
                # Process each resolvent
                for resolvent, eliminated in resolvent_pairs:
                    stats['clauses_generated'] += 1
                    if resolvent not in clause_set:
                        if mode:
                            step_counter += 1
                            stats["steps"] = step_counter
                            print(f"  {Fore.YELLOW}Step {step_counter}:{Style.RESET_ALL} Resolving {Fore.MAGENTA}{format_clause(c1)}{Style.RESET_ALL} and {Fore.MAGENTA}{format_clause(c2)}{Style.RESET_ALL}")
                            print(f"    {Fore.BLUE}Derived:{Style.RESET_ALL} {Fore.GREEN}{format_clause(resolvent)}{Style.RESET_ALL}")
                            print(f"    {Fore.RED}(Eliminated: {eliminated}){Style.RESET_ALL}")
                        
                        new_resolvents.add(resolvent)
                        
                        # Check for empty clause immediately
                        if len(resolvent) == 0:
                            if mode:
                                print(f"{Fore.GREEN}Empty clause found! Contradiction achieved.{Style.RESET_ALL}")
                            
                            end_time = time.time()
                            time_taken = end_time - start_time
                            
                            # Final memory check
                            current_memory = get_memory_usage()
                            peak_memory = max(peak_memory, current_memory)
                            
                            # Stop loading indicator if it's running
                            if loading:
                                loading.stop()
                            
                            stats["final_clause_count"] = len(clause_set) + len(set(new_resolvents)) 
                            
                            return True, time_taken, peak_memory, stats
                
                # Regular memory check during resolution
                current_memory = get_memory_usage()
                peak_memory = max(peak_memory, current_memory)
            
        # Add new resolvents to clause set
        clause_set.update(new_resolvents)
    
    # If we get here without finding an empty clause, the KB doesn't entail the query
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Final memory check
    current_memory = get_memory_usage()
    peak_memory = max(peak_memory, current_memory)
    
    # Stop loading indicator if it's running
    if loading:
        loading.stop()
    
    stats["steps"] = step_counter
    stats["final_clause_count"] = len(clause_set)
    
    return False, time_taken, peak_memory, stats