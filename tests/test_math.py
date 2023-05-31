


import unittest

import numpy as np
from sklearn import preprocessing
from utils.math import Math

class TestMath(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = np.array([[3.0, 4.0, 5.0],
                                [2.0, 5.0, 1.0],
                                [4.0, 2.0, 3.0],
                                [1.0, 3.0, 2.0]])
        self.weights = [0.5, 0.3, 0.2]

    def test_weighted_matrix(self):
        weighted_matrix = np.array([[1.5, 1.2, 1.0],
                                    [1.0, 1.5, 0.2],
                                    [2.0, 0.6, 0.6],
                                    [0.5, 0.9, 0.4]])
        np.testing.assert_allclose(Math.weighted_matrix(self.matrix, self.weights), weighted_matrix)

    def test_euclidean_distance_same_matrix(self):
        matrix = np.array([[1, 2], [3, 4]])
        expected_distance = 0.0

        distance = Math.calculate_euclidean_distance(matrix, matrix)

        self.assertAlmostEqual(distance, expected_distance)

    def test_euclidean_distance_different_matrices(self):
        matrix1 = np.array([[1, 2], [3, 4]])
        matrix2 = np.array([[2, 3], [4, 5]])
        expected_distance = 2

        distance = Math.calculate_euclidean_distance(matrix1, matrix2)

        self.assertAlmostEqual(distance, expected_distance)

    def test_euclidean_distance_matrices_with_different_shapes(self):
        matrix1 = np.array([[1, 2, 3], [4, 5, 6]])
        matrix2 = np.array([[2, 3], [4, 5]])
        
        with self.assertRaises(ValueError):
            Math.calculate_euclidean_distance(matrix1, matrix2)


class TestTOPSIS(unittest.TestCase):
    def setUp(self):
        self.decision_matrix = Math.DecisionMatrixBuilder()
        self.decision_matrix.matrix = np.array([[3.0, 4.0, 5.0],
                                         [2.0, 5.0, 1.0],
                                         [4.0, 2.0, 3.0],
                                         [1.0, 3.0, 2.0]])
        self.decision_matrix.criteria_dict = {
            "C1": 0,
            "C2": 1,
            "C3": 2
        }
        self.decision_matrix.alternatives_dict = {
            "A1": 0,
            "A2": 1,
            "A3": 2,
            "A4": 3
        }
        self.weights = [0.5, 0.3, 0.2]
        self.impacts = [Math.TOPSIS.MAX, Math.TOPSIS.MAX, Math.TOPSIS.MIN]
        self.topsis = Math.TOPSIS(self.decision_matrix, self.weights, self.impacts)
        self.topsis.topsis()

    def test_ideal_best_worst(self):
        ideal_solution = np.array([2.0, 1.5, 0.2])
        anti_ideal_solution = np.array([0.5, 0.6, 1.0])
        np.testing.assert_array_equal(self.topsis._ideal, ideal_solution)
        np.testing.assert_array_equal(self.topsis._anti_ideal, anti_ideal_solution)

    
    def test_euclidean_distances(self):
        distances = np.array([[0.989949, 1.16619],
                              [1.0, 1.30384],
                              [0.984886, 1.552417],
                              [1.627882, 0.67082]])
        np.testing.assert_allclose(self.topsis._distances, distances, atol=1e-3)

    def test_relative_closeness(self):
        closeness = np.array([0.54087, 0.565942, 0.611838, 0.291826])
        np.testing.assert_allclose(self.topsis._closeness, closeness, atol=1e-3)

    def test_get_closeness(self):
        closeness = np.array([0.54087, 0.565942, 0.611838, 0.291826])
        np.testing.assert_allclose(self.topsis.get_closeness(), closeness, atol=1e-3)

    def test_get_ranking(self):
        ranking = np.array([3, 2, 1, 4])
        np.testing.assert_array_equal(self.topsis.get_ranking(), ranking)

class TestDecisionMatrixBuilder(unittest.TestCase):

    def test_add_criteria(self):
        builder = Math.DecisionMatrixBuilder()
        criteria = np.array([[3, 4, 5]])
        label = "Criterion 1"
        builder.add_criteria(criteria, label)
        
        self.assertEqual(len(builder.criteria), 1)
        self.assertEqual(len(builder.criteria_label), 1)
        self.assertTrue(np.allclose(builder.criteria[0], preprocessing.normalize(criteria)))
        self.assertEqual(builder.criteria_label[0], label)

    def test_add_alternative(self):
        builder = Math.DecisionMatrixBuilder()
        alternative = np.array([[2, 5, 1]])
        label = "Alternative 1"
        builder.add_alternative(alternative, label)
        
        self.assertEqual(len(builder.alternatives), 1)
        self.assertEqual(len(builder.alternatives_label), 1)
        self.assertTrue(np.allclose(builder.alternatives[0], preprocessing.normalize(alternative)))
        self.assertEqual(builder.alternatives_label[0], label)

    def test_build(self):
        builder = Math.DecisionMatrixBuilder()
        criteria1 = np.array([[3, 4, 5]])
        criteria2 = np.array([[1, 2, 3]])
        alternative1 = np.array([[2, 5, 1]])
        alternative2 = np.array([[4, 2, 3]])
        builder.add_criteria(criteria1, "Criterion 1")
        builder.add_criteria(criteria2, "Criterion 2")
        builder.add_alternative(alternative1, "Alternative 1")
        builder.add_alternative(alternative2, "Alternative 2")
        matrix = builder.build()
        
        self.assertIsNotNone(matrix)
        self.assertEqual(matrix.matrix.shape, (2, 2))
