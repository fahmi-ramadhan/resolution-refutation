import time
import psutil
import os
from colorama import Fore, Style

# Assuming these are unchanged
from parser import forward_slice
from loading_indicator import LoadingIndicator

def clause_to_frozenset(sentence):
    m = set()
    j = 1 if sentence[0] == "(" else 0
    L = len(sentence) - 1 if sentence[0] == "(" else len(sentence)
    while j < L:
        literal, j = forward_slice(sentence, j)
        if literal[0] == "!":
            m.add("!" + str(literal[1]))
        else:
            m.add(str(literal[0]))
        j += 2
    return frozenset(m)

def format_clause(clause):
    return "[" + ", ".join(sorted(clause)) + "]"

def resolve_clause_pair(clause1, clause2):
    resolvents = []
    for literal in clause1:
        neg_literal = literal[1:] if literal.startswith("!") else "!" + literal
        if neg_literal in clause2:
            new_clause = frozenset(clause1.difference({literal}).union(clause2.difference({neg_literal})))
            eliminated_pair = f"{literal}/{neg_literal}"
            resolvents.append((new_clause, eliminated_pair))
    return resolvents

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)

def is_subsumed(new_clause, clause_set):
    return any(existing.issubset(new_clause) for existing in clause_set)

def subsumes_any(new_clause, clause_set):
    return [existing for existing in clause_set if new_clause.issubset(existing)]

def resolve(sentence, mode):
    start_time = time.time()
    initial_memory = get_memory_usage()
    peak_memory = initial_memory

    loading = None
    if not mode:
        loading = LoadingIndicator("Performing resolution")
        loading.start()

    stats = {
        "steps": 0,
        "clauses_generated": 0,
        "clause_pairs_examined": 0,
        "subsumed_clauses_removed": 0
    }

    # Convert sentence to clause set
    clause_set = set()
    clause = []
    for literal in sentence:
        if literal == "&":
            clause_set.add(clause_to_frozenset(clause))
            clause.clear()
        else:
            clause.append(literal)
    clause_set.add(clause_to_frozenset(clause))

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

        for c1 in worklist:
            for c2 in clause_set:
                stats["clause_pairs_examined"] += 1
                resolvent_pairs = resolve_clause_pair(c1, c2)

                for resolvent, eliminated in resolvent_pairs:
                    stats["clauses_generated"] += 1

                    if resolvent not in clause_set and not is_subsumed(resolvent, clause_set):
                        # Collect subsumed clauses to remove later
                        subsumed = subsumes_any(resolvent, clause_set)
                        if subsumed:
                            clauses_to_remove.update(subsumed)

                        new_resolvents.add(resolvent)

                        if mode:
                            step_counter += 1
                            stats["steps"] = step_counter
                            print(f"  {Fore.YELLOW}Step {step_counter}:{Style.RESET_ALL} Resolving {Fore.MAGENTA}{format_clause(c1)}{Style.RESET_ALL} and {Fore.MAGENTA}{format_clause(c2)}{Style.RESET_ALL}")
                            print(f"    {Fore.BLUE}Derived:{Style.RESET_ALL} {Fore.GREEN}{format_clause(resolvent)}{Style.RESET_ALL}")
                            print(f"    {Fore.RED}(Eliminated: {eliminated}){Style.RESET_ALL}")
                            if subsumed:
                                print(f"    {Fore.CYAN}(Removed subsumed: {', '.join(format_clause(s) for s in subsumed)}){Style.RESET_ALL}")

                        if len(resolvent) == 0:
                            if mode:
                                print(f"{Fore.GREEN}Empty clause found! Contradiction achieved.{Style.RESET_ALL}")
                            end_time = time.time()
                            time_taken = end_time - start_time
                            peak_memory = max(peak_memory, get_memory_usage())
                            if loading:
                                loading.stop()
                            stats["final_clause_count"] = len(clause_set) + len(new_resolvents) - len(clauses_to_remove)
                            return True, time_taken, peak_memory, stats

        # Apply updates after iteration
        clause_set.difference_update(clauses_to_remove)
        stats["subsumed_clauses_removed"] += len(clauses_to_remove)
        clause_set.update(new_resolvents)
        worklist = new_resolvents

        peak_memory = max(peak_memory, get_memory_usage())

        if not new_resolvents:
            break

    end_time = time.time()
    time_taken = end_time - start_time
    peak_memory = max(peak_memory, get_memory_usage())
    if loading:
        loading.stop()
    stats["final_clause_count"] = len(clause_set)

    return False, time_taken, peak_memory, stats

# # Example usage
# if __name__ == "__main__":
#     sentence = ["(", "A", ")", "&", "(", "!A", "|", "B", ")", "&", "(", "!B", ")"]
#     result, time_taken, peak_memory, stats = resolve(sentence, mode=True)
#     print(f"\nResult: {result}, Time: {time_taken:.3f}s, Peak Memory: {peak_memory:.2f}MB")
#     print(f"Stats: {stats}")