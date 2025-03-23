"""
Enhanced resolver module for propositional logic resolution.

This module implements an optimized resolution algorithm for propositional logic,
featuring subsumption checking, more efficient clause management, and additional
statistics tracking. It is designed to be used as an alternative to the original
resolver implementation.
"""

import time
from colorama import Fore, Style
from loading_indicator import LoadingIndicator
from resolver import clause_to_frozenset, format_clause, resolve_clause_pair, get_memory_usage

def is_subsumed(new_clause, clause_set):
    """
    Check if a new clause is subsumed by any existing clause in the clause set.
    
    A clause C1 subsumes another clause C2 if C1 is a subset of C2. This means 
    C1 is more general than C2, and we can safely ignore C2.
    For later application, if the new clause is subsumed by any existing clause,
    we can avoid adding the new clause to the clause set.
    
    Args:
        new_clause (frozenset): The new clause to check for subsumption
        clause_set (set): The set of existing clauses
        
    Returns:
        bool: True if the new clause is subsumed by any existing clause, False otherwise
    """
    return any(existing.issubset(new_clause) for existing in clause_set)

def subsumes_any(new_clause, clause_set):
    """
    Find all clauses in the clause set that are subsumed by the new clause.
    
    For each existing clause in the clause set, check if the new clause is a subset
    of the existing clause. If so, the new clause subsumes the existing clause, and those existing
    clauses can be removed.

    Args:
        new_clause (frozenset): The new clause that may subsume others
        clause_set (set): The set of existing clauses to check against
        
    Returns:
        list: List of clauses that are subsumed by the new clause
    """
    return [existing for existing in clause_set if new_clause.issubset(existing)]

def resolve(sentence, mode):
    """
    Perform resolution on a set of propositional logic clauses.
    
    This enhanced resolver implements several optimizations:
    1. Subsumption checking to eliminate redundant clauses
    2. More efficient clause management with workset approach
    3. Detailed statistics tracking
    
    Args:
        sentence (list): List of literals and connectives in the knowledge base 
                         and negated query
        mode (bool): Whether to print detailed resolution steps
    
    Returns:
        tuple: (result, time_taken, peak_memory, stats)
            - result (bool): True if a contradiction was found (meaning entailment), 
                            False otherwise
            - time_taken (float): Execution time in seconds
            - peak_memory (float): Peak memory usage in MB
            - stats (dict): Dictionary containing resolution statistics
    """
    start_time = time.time()
    initial_memory = get_memory_usage()
    peak_memory = initial_memory

    # Memory check frequency control - check every N iterations
    memory_check_frequency = 1000
    iteration_counter = 0

    # Initialize loading indicator if not in verbose mode
    loading = None
    if not mode:
        loading = LoadingIndicator("Performing resolution")
        loading.start()

    # Statistics tracking
    stats = {
        "clauses_generated": 0,
        "clause_pairs_examined": 0,
    }

    # Convert sentence to clause set
    clause_set = set()
    clause = []

    # Process the sentence into clauses in frozenset form
    for literal in sentence:
        if literal == "&":
            clause_set.add(clause_to_frozenset(clause))
            clause.clear()
        else:
            clause.append(literal)
    
    # Add the last clause
    clause_set.add(clause_to_frozenset(clause))

    # Display initial clauses in verbose mode
    if mode:
        print(f"{Fore.CYAN}KB ∪ ¬Q:{Style.RESET_ALL}")
        formatted_clauses = [f"{Fore.MAGENTA}[{', '.join(clause)}]{Style.RESET_ALL}" for clause in clause_set]
        print(f"  {{{', '.join(formatted_clauses)}}}")
        print(f"\n{Fore.CYAN}Resolution steps:{Style.RESET_ALL}")

    stats["initial_clauses"] = len(clause_set)
    worklist = clause_set.copy()
    step_counter = 0

    while worklist:
        new_resolvents = set()
        clauses_to_remove = set()  # Track clauses to remove due to subsumption

        # Check memory usage only at the start of each main iteration
        if iteration_counter % memory_check_frequency == 0:
            current_memory = get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
        
        iteration_counter += 1

        #Try to resolve each clause in the worklist with all clauses in the main clause set/KB
        for c1 in worklist:
            for c2 in clause_set:
                stats["clause_pairs_examined"] += 1
                resolvent_pairs = resolve_clause_pair(c1, c2)

                # Process each resolvent
                for resolvent, eliminated in resolvent_pairs:
                    stats["clauses_generated"] += 1

                    if resolvent not in clause_set and not is_subsumed(resolvent, clause_set):
                        # Collect subsumed clauses to remove later
                        subsumed = subsumes_any(resolvent, clause_set)
                        if subsumed:
                            clauses_to_remove.update(subsumed)

                        new_resolvents.add(resolvent)

                        # Display resolution step in verbose mode
                        if mode:
                            step_counter += 1
                            print(f"  {Fore.YELLOW}Step {step_counter}:{Style.RESET_ALL} Resolving {Fore.MAGENTA}{format_clause(c1)}{Style.RESET_ALL} and {Fore.MAGENTA}{format_clause(c2)}{Style.RESET_ALL}")
                            print(f"    {Fore.BLUE}Derived:{Style.RESET_ALL} {Fore.GREEN}{format_clause(resolvent)}{Style.RESET_ALL}")
                            print(f"    {Fore.RED}(Eliminated: {eliminated}){Style.RESET_ALL}")
                            if subsumed:
                                print(f"    {Fore.CYAN}(Clauses subsumed: {', '.join(format_clause(s) for s in subsumed)}){Style.RESET_ALL}")

                        # Check for empty clause immediately
                        if len(resolvent) == 0:
                            if mode:
                                print(f"{Fore.GREEN}Empty clause found! Contradiction achieved.{Style.RESET_ALL}")

                            end_time = time.time()
                            time_taken = end_time - start_time

                            # Final memory check
                            peak_memory = max(peak_memory, get_memory_usage())

                            # Stop loading indicator if it's running
                            if loading:
                                loading.stop()

                            stats["final_clause_count"] = len(clause_set) + len(new_resolvents)

                            return True, time_taken, peak_memory, stats

        # Remove subsumed clauses and update the clause set
        clause_set.difference_update(clauses_to_remove)
        clause_set.update(new_resolvents)
        worklist = new_resolvents  # Only process new resolvents in the next iteration

        # If no new resolvents were generated, we've reached a fixed point
        if not new_resolvents:
            break

    # If we get here without finding an empty clause, the KB doesn't entail the query
    end_time = time.time()
    time_taken = end_time - start_time

    # Final memory check
    peak_memory = max(peak_memory, get_memory_usage())

    # Stop loading indicator if it's running
    if loading:
        loading.stop()

    stats["final_clause_count"] = len(clause_set)

    return False, time_taken, peak_memory, stats
