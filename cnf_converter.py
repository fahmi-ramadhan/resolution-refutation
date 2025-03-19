"""
CNF Converter module for propositional logic resolution prover.
Converts propositional logic formulas to Conjunctive Normal Form (CNF).
"""

from parser import forward_slice, backward_slice


def induce_parenthesis(sentence):
    """
    Induces parentheses in a propositional formula according to operator precedence.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula with parentheses inserted based on operator precedence
    """
    sentence = around_unary_op(sentence, "!")
    sentence = around_binary_op(sentence, "&")
    sentence = around_binary_op(sentence, "|")
    sentence = around_binary_op(sentence, ">")
    sentence = around_binary_op(sentence, "=")
    return sentence


def around_unary_op(sentence, op):
    """
    Places parentheses around expressions with unary operators.
    
    Args:
        sentence (list): Tokenized propositional formula
        op (str): Unary operator (e.g., "!")
    
    Returns:
        list: Formula with parentheses added around unary operations
    """
    processed_sentence = []
    i = 0
    while i < len(sentence):
        if sentence[i] == op:
            i += 1
            sentence_slice, i = forward_slice(sentence, i)
            sentence_slice = around_unary_op(sentence_slice, op)
            processed_sentence += ["(", "!"] + sentence_slice.copy() + [")"]
        else:
            processed_sentence.append(sentence[i])
        i += 1
    return processed_sentence


def around_binary_op(sentence, op):
    """
    Places parentheses around expressions with binary operators.
    
    Args:
        sentence (list): Tokenized propositional formula
        op (str): Binary operator (e.g., "&", "|", ">", "=")
    
    Returns:
        list: Formula with parentheses added around binary operations
    """
    processed_sentence = []
    i = 0
    while i < len(sentence):
        if sentence[i] == op:
            A, processed_sentence = backward_slice(processed_sentence)
            A = around_binary_op(A, op)
            i += 1
            sentence_slice, i = forward_slice(sentence, i)
            sentence_slice = around_binary_op(sentence_slice, op)
            processed_sentence += (
                ["("] + A.copy() + [op] + sentence_slice.copy() + [")"]
            )
        else:
            processed_sentence.append(sentence[i])
        i += 1
    return processed_sentence


def literal_not_protected(sentence):
    """
    Checks if there's a literal in the sentence that is not protected by parentheses.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        bool: True if there's an unprotected literal, False otherwise
    """
    from parser import OPERATORS
    
    if not any(i in OPERATORS for i in sentence):
        return False

    off_balance = 0
    for _, token in enumerate(sentence):
        if token == "(":
            off_balance += 1
        elif token == ")":
            off_balance -= 1
        elif off_balance == 0:
            return True

    return False


def eliminate_invalid_parenthesis(sentence):
    """
    Eliminates unnecessary parentheses from a propositional formula.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula with unnecessary parentheses removed
    """
    processed_sentence = []
    brackets = []
    content = []

    for _, token in enumerate(sentence):
        if token == "(":
            content.append(processed_sentence.copy())
            brackets.append("(")
            processed_sentence.clear()
        elif token == ")" and content:
            if literal_not_protected(processed_sentence):
                processed_sentence = ["("] + processed_sentence + [")"]
            processed_sentence = content[len(content) - 1].copy() + processed_sentence
            brackets.pop()
            content.pop()
        else:
            processed_sentence.append(token)

    return processed_sentence


def iff_equivalent(A, B):
    """
    Returns ((A>B)&(B>A)) as equivalent of (A=B).
    
    Args:
        A (list): Tokenized propositional formula
        B (list): Tokenized propositional formula
    
    Returns:
        list: Equivalent formula for A=B in terms of implications
    """
    return (
        ["(", "("]
        + A.copy()
        + [">"]
        + B.copy()
        + [")", "&", "("]
        + B.copy()
        + [">"]
        + A.copy()
        + [")", ")"]
    )


def implies_equivalent(A, B):
    """
    Returns ((!A)|B) as equivalent of (A>B).
    
    Args:
        A (list): Tokenized propositional formula
        B (list): Tokenized propositional formula
    
    Returns:
        list: Equivalent formula for A>B in terms of negation and disjunction
    """
    return ["(", "(", "!"] + A.copy() + [")", "|"] + B.copy() + [")"]


def eliminate_op(sentence, op):
    """
    Eliminates complex operators (= and >) from a propositional formula.
    
    Args:
        sentence (list): Tokenized propositional formula
        op (str): Operator to eliminate (e.g., "=", ">")
    
    Returns:
        list: Formula with the specified operator eliminated
    """
    processed_sentence = []
    i = 0
    while i < len(sentence):
        if sentence[i] == op:
            A, processed_sentence = backward_slice(processed_sentence)
            i += 1
            B, i = forward_slice(sentence, i)
            A = eliminate_op(A, op)
            B = eliminate_op(B, op)
            processed_sentence += (
                iff_equivalent(A, B) if op == "=" else implies_equivalent(A, B)
            ).copy()
        else:
            processed_sentence.append(sentence[i])
        i += 1
    return processed_sentence


def move_not_inwards(sentence):
    """
    Moves negations inward using De Morgan's laws.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula with negations moved inward
    """
    processed_sentence = []

    while True:
        processed_sentence = []
        i = 0
        while i < len(sentence):
            if sentence[i] == "!":
                i += 1
                B, i = forward_slice(sentence, i)
                if B[0] == "(":
                    processed_sentence.append("(")
                    j = 1
                    while j < len(B):
                        tmp, j = forward_slice(B, j)
                        tmp.pop(0) if tmp[0] == "!" else tmp.insert(0, "!")
                        processed_sentence += tmp.copy()
                        j += 1
                        if j < len(B) - 1:
                            processed_sentence += (
                                ["&"] if B[j] == "|" else ["|"] if (B[j] == "&") else []
                            )
                        j += 1
                    processed_sentence.append(")")
                else:
                    B.pop(0) if B[0] == "!" else processed_sentence.append("!")
                    processed_sentence += B.copy()
            else:
                processed_sentence.append(sentence[i])
            i += 1

        if processed_sentence == sentence:
            break
        sentence = processed_sentence

    return processed_sentence


def distribute_or_over_and(sentence):
    """
    Distributes OR over AND to convert to CNF.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula with OR distributed over AND
    """
    processed_sentence = []

    i = 0
    while i < len(sentence):
        if sentence[i] == "|":
            A, processed_sentence = backward_slice(processed_sentence)
            A = distribute_or_over_and(A)

            tmp3 = []
            if A[0] == "(":
                j = 1
                while j < (len(A) - 1):
                    tmp, j = forward_slice(A, j)
                    tmp3.append(tmp.copy())
                    j += 2
            else:
                tmp3.append(A.copy())

            i += 1
            assert i < len(sentence)

            B, i = forward_slice(sentence, i)
            B = distribute_or_over_and(B)

            tmp2 = []
            if B[0] == "(":
                j = 1
                while j < (len(B) - 1):
                    tmp, j = forward_slice(B, j)
                    tmp2.append(tmp.copy())
                    j += 2
            else:
                tmp2.append(B.copy())

            for k in range(0, len(tmp2)):
                for m in range(0, len(tmp3)):
                    processed_sentence += (
                        ["("]
                        + tmp3[m].copy()
                        + ["|"]
                        + tmp2[k].copy()
                        + [")"]
                        + (["&"] if m != len(tmp3) - 1 else [])
                    )
                processed_sentence += ["&"] if k != len(tmp2) - 1 else []
        else:
            processed_sentence.append(sentence[i])

        i += 1

    return processed_sentence


def _process_operand(operand):
    """
    Processes an operand by removing unnecessary parentheses.
    
    Args:
        operand (list): Tokenized propositional formula
    
    Returns:
        list: Processed operand
    """
    operand = eliminate_invalid_parenthesis(operand)
    if operand[0] == "(":
        return (
            ["("]
            + [j for j in operand[1 : len(operand) - 1] if j not in ["(", ")"]]
            + [")"]
        )
    else:
        return [j for j in operand[0 : len(operand)] if j not in ["(", ")"]]


def split_around_and(sentence):
    """
    Splits a sentence around AND operators.
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula split around AND operators
    """
    processed_sentence = []
    operand = []

    for _, token in enumerate(sentence):
        if token == "&":
            processed_sentence += _process_operand(operand).copy()
            processed_sentence.append("&")
            operand.clear()
        else:
            operand.append(token)

    return processed_sentence + _process_operand(operand).copy()


def to_cnf(sentence):
    """
    Converts a propositional formula to Conjunctive Normal Form (CNF).
    
    Args:
        sentence (list): Tokenized propositional formula
    
    Returns:
        list: Formula in CNF
    """
    sentence = induce_parenthesis(sentence)
    sentence = eliminate_invalid_parenthesis(sentence)
    sentence = eliminate_op(sentence, "=")
    sentence = eliminate_invalid_parenthesis(sentence)
    sentence = eliminate_op(sentence, ">")
    sentence = eliminate_invalid_parenthesis(sentence)
    sentence = move_not_inwards(sentence)
    sentence = eliminate_invalid_parenthesis(sentence)

    prev = []
    while prev != sentence:
        prev = sentence
        sentence = distribute_or_over_and(sentence)
        sentence = eliminate_invalid_parenthesis(sentence)

    return split_around_and(sentence)
