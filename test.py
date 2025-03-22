"""
Test module for propositional logic resolution prover.
Contains unit tests for the parser, CNF converter, and resolver modules.
"""

import unittest
from parser import segment_sentence, forward_slice, backward_slice
from cnf_converter import to_cnf, induce_parenthesis, around_unary_op, around_binary_op
from cnf_converter import literal_not_protected, eliminate_invalid_parenthesis
from cnf_converter import iff_equivalent, implies_equivalent, eliminate_op
from cnf_converter import move_not_inwards, distribute_or_over_and, split_around_and
from resolver import resolve


class TestParser(unittest.TestCase):
    """Tests for the parser module."""

    def test_segment_sentence(self):
        """Test segmenting a propositional logic sentence."""
        sentence = "A & (B | !C)"
        expected = ['A', '&', '(', 'B', '|', '!', 'C', ')']
        self.assertEqual(segment_sentence(sentence), expected)

    def test_forward_slice(self):
        """Test forward slicing."""
        sentence = ['A', '&', '(', 'B', '|', '(', '!', 'C', '&', 'D', ')', ')']
        # Test slicing from index 2 (from the first open parenthesis)
        slice_result, new_index = forward_slice(sentence, 2)
        self.assertEqual(slice_result, ['(', 'B', '|', '(', '!', 'C', '&', 'D', ')', ')'])
        self.assertEqual(new_index, 11)

        # Test slicing from index 3 (from B)
        slice_result, new_index = forward_slice(sentence, 3)
        self.assertEqual(slice_result, ['B'])
        self.assertEqual(new_index, 3)

        # Test slicing empty sentence 
        slice_result, new_index = forward_slice([], 0)
        self.assertEqual(slice_result, [])
        self.assertEqual(new_index, 0)

    def test_backward_slice(self):
        """Test backward slicing."""
        sentence = ['A', '(', 'B', '(', '!', 'C', '&', 'D', ')', ')']
        slice_result, remaining = backward_slice(sentence)
        self.assertEqual(slice_result, ['(', 'B', '(', '!', 'C', '&', 'D', ')', ')'])
        self.assertEqual(remaining, ['A'])

        # Test slicing empty sentence 
        slice_result, remaining = backward_slice([])
        self.assertEqual(slice_result, [])
        self.assertEqual(remaining, [])


class TestCNFConverter(unittest.TestCase):
    """Tests for the CNF converter module."""

    def test_induce_parenthesis(self):
        """Test inducing parentheses based on operator precedence."""
        sentence = segment_sentence("A & B | C")
        result = induce_parenthesis(sentence)
        self.assertEqual(''.join(result), '((A&B)|C)')

        sentence = segment_sentence("A | B & C")
        result = induce_parenthesis(sentence)
        self.assertEqual(''.join(result), '(A|(B&C))')

        sentence = segment_sentence("!A & B")
        result = induce_parenthesis(sentence)
        self.assertEqual(''.join(result), '((!A)&B)')

    def test_around_unary_op(self):
        """Test placing parentheses around unary operators."""
        sentence = segment_sentence("!A")
        result = around_unary_op(sentence, "!")
        self.assertEqual(''.join(result), '(!A)')

        sentence = segment_sentence("!!A")
        result = around_unary_op(sentence, "!")
        self.assertEqual(''.join(result), '(!(!A))')

    def test_around_binary_op(self):
        """Test placing parentheses around binary operators."""
        sentence = segment_sentence("A & B & C")
        result = around_binary_op(sentence, "&")
        self.assertEqual(''.join(result), '(((A&B))&C)')

        sentence = segment_sentence("A | B | C")
        result = around_binary_op(sentence, "|")
        self.assertEqual(''.join(result), '(((A|B))|C)')

    def test_literal_not_protected(self):
        """Test checking if literals are protected by parentheses."""
        sentence = segment_sentence("A & B")
        self.assertTrue(literal_not_protected(sentence))

        sentence = segment_sentence("(A & B)")
        self.assertFalse(literal_not_protected(sentence))

        sentence = segment_sentence("A")
        self.assertFalse(literal_not_protected(sentence))

    def test_eliminate_invalid_parenthesis(self):
        """Test elimination of unnecessary parentheses."""
        sentence = segment_sentence("((A & B))")
        result = eliminate_invalid_parenthesis(sentence)
        self.assertEqual(''.join(result), '(A&B)')

        sentence = segment_sentence("(A) & (B)")
        result = eliminate_invalid_parenthesis(sentence)
        self.assertEqual(''.join(result), 'A&B')

    def test_iff_equivalent(self):
        """Test conversion of iff (=) to equivalent form."""
        A = segment_sentence("A")
        B = segment_sentence("B")
        result = iff_equivalent(A, B)
        self.assertEqual(''.join(result), '((A>B)&(B>A))')

    def test_implies_equivalent(self):
        """Test conversion of implies (>) to equivalent form."""
        A = segment_sentence("A")
        B = segment_sentence("B")
        result = implies_equivalent(A, B)
        self.assertEqual(''.join(result), '((!A)|B)')

    def test_eliminate_op(self):
        """Test elimination of operators."""
        sentence = segment_sentence("A = B")
        result = eliminate_op(sentence, "=")
        self.assertEqual(''.join(result), '((A>B)&(B>A))')

        sentence = segment_sentence("A > B")
        result = eliminate_op(sentence, ">")
        self.assertEqual(''.join(result), '((!A)|B)')

    def test_move_not_inwards(self):
        """Test moving negations inward using De Morgan's laws."""
        sentence = segment_sentence("!(A & B)")
        result = move_not_inwards(sentence)
        self.assertEqual(''.join(result), '(!A|!B)')

        sentence = segment_sentence("!(A | B)")
        result = move_not_inwards(sentence)
        self.assertEqual(''.join(result), '(!A&!B)')

        sentence = segment_sentence("!!A")
        result = move_not_inwards(sentence)
        self.assertEqual(''.join(result), 'A')

    def test_distribute_or_over_and(self):
        """Test distributing OR over AND."""
        sentence = segment_sentence("A | (B & C)")
        result = distribute_or_over_and(sentence)
        self.assertEqual(''.join(result), '(A|B)&(A|C)')

        sentence = segment_sentence("(A & B) | C")
        result = distribute_or_over_and(sentence)
        self.assertEqual(''.join(result), '(A|C)&(B|C)')

        sentence = segment_sentence("(A & B) | (C & D)")
        result = distribute_or_over_and(sentence)
        self.assertEqual(''.join(result), '(A|C)&(B|C)&(A|D)&(B|D)')

    def test_split_around_and(self):
        """Test splitting a sentence around AND operators."""
        sentence = segment_sentence("A & B & C")
        result = split_around_and(sentence)
        self.assertEqual(''.join(result), 'A&B&C')

        sentence = segment_sentence("(A | B) & (C | D)")
        result = split_around_and(sentence)
        self.assertEqual(''.join(result), '(A|B)&(C|D)')


class TestResolver(unittest.TestCase):
    """Tests for the resolver module."""

    def test_resolution_true(self):
        """Test resolution that should return True."""
        kb = "A & B"
        query = "A"
        kb_cnf = to_cnf(segment_sentence(kb))
        neg_query_cnf = to_cnf(segment_sentence("!("+query+")"))
        result, _, _, _ = resolve(kb_cnf + ['&'] + neg_query_cnf, True)
        self.assertTrue(result)

    def test_resolution_false(self):
        """Test resolution that should return False."""
        kb = "A & B"
        query = "C"
        kb_cnf = to_cnf(segment_sentence(kb))
        neg_query_cnf = to_cnf(segment_sentence("!("+query+")"))
        result, _, _, _ = resolve(kb_cnf + ['&'] + neg_query_cnf, False)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
