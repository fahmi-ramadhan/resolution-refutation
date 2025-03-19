"""
Parser module for propositional logic resolution prover.
Handles tokenization and parsing of propositional logic formulas.
"""

import sys


OPERATORS = ["!", "&", "|", ">", "=", "(", ")"]

def segment_sentence(sentence):
    """
    Tokenizes a propositional logic sentence into a list of tokens.
    
    Args:
        sentence (str): A string representing a propositional logic formula
    
    Returns:
        list: A list of tokens (operators and literals)
    
    Example:
        >>> segment_sentence("A & (B | !C)")
        ['A', '&', '(', 'B', '|', '!', 'C', ')']
    """
    segmented_sentence = []

    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] in OPERATORS:
            segmented_sentence.append(sentence[i])
            i += 1
        elif sentence[i] == " ":
            i += 1
        else:
            literal = ""
            while i < L and not sentence[i] in OPERATORS and sentence[i] != " ":
                literal += sentence[i]
                i += 1
            segmented_sentence.append(literal)

    return segmented_sentence


def forward_slice(sentence, index):
    """
    Returns forward slice of sentence beginning from index.

    A forward slice is defined as the next complete segment in the sentence.
    
    Args:
        sentence (list): Tokenized propositional formula
        index (int): Index from which slicing should begin (included)
    
    Returns:
        tuple: (forward_slice, new_index) where forward_slice is the sliced segment and
               new_index is the index after the slice
    
    Examples:
        Forward Slice from index = 2 of "A&(B|(!C&D))" is "(B|(!C&D))"
        Forward Slice from index = 3 of "A&(B|(!C&D))" is "B"
        Forward Slice from index = 5 of "A&(B|(!C&D))" is "(!C&D)"
        Forward Slice from index = 6 of "A&(B|(!C&D))" is "!C"
    """
    off_balance = 0
    i = index

    while i < len(sentence):
        off_balance += 1 if sentence[i] == "(" else -1 if sentence[i] == ")" else 0
        if off_balance == 0 and sentence[i] != "!":
            return sentence[index : (i + 1)], i
        i += 1
    return sentence[index:], i


def backward_slice(sentence):
    """
    Returns backward slice of sentence.

    A backward slice is defined as the previous complete segment in the sentence.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        tuple: (backward_slice, remaining) where backward_slice is the sliced segment and
               remaining is the remainder of the sentence
    
    Examples:
        Backward Slice of "A&(B|(!C&D))" is "(B|(!C&D))"
        Backward Slice of "B|(!C&D)" is "(!C&D)"
        Backward Slice of "!C&D" is "D"
        Backward Slice of "!C" is "!C"
    """
    off_balance = 0
    L = len(sentence)
    i = L - 1

    while i >= 0:
        off_balance += 1 if sentence[i] == ")" else -1 if sentence[i] == "(" else 0
        if off_balance == 0:
            i -= 1 if i > 0 and sentence[i - 1] == "!" else 0
            return sentence[i:L], sentence[0:i]
        i -= 1
    return sentence, []
