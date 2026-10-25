"""Run the actual Python blocks embedded in the ML 101 practice cards."""
from pathlib import Path
import math
import random
import re
import unittest
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "content/handbooks/ml-101/questions"


def load_card(relative):
    text = (QUESTIONS / relative).read_text()
    blocks = re.findall(r"```python\n(.*?)\n```", text, re.S)
    assert blocks, f"No Python block in {relative}"
    namespace = {}
    exec(compile("\n\n".join(blocks), str(QUESTIONS / relative), "exec"), namespace)
    return namespace


knn = load_card("classical-models/ml101-knn-implementation.md")["knn_predict"]
Bigram = load_card("probability/ml101-bigram-prediction.md")["BigramPredictor"]
kmeans = load_card("unsupervised/ml101-kmeans-implementation.md")["kmeans"]
NGramLM = load_card("probability/ml101-ngram-generation.md")["NGramLM"]
wordpiece = load_card("data/ml101-wordpiece-implementation.md")["wordpiece_encode"]
gmm_namespace = load_card("unsupervised/ml101-em-worked-step.md")
em_step = gmm_namespace["gmm_em_step"]
mlp_namespace = load_card("neural-networks/ml101-mlp-backprop-implementation.md")
mlp = mlp_namespace["mlp_loss_grad"]
train_step = mlp_namespace["mlp_train_step"]
softmax_namespace = load_card("neural-networks/ml101-softmax-backward.md")
softmax = softmax_namespace["softmax_forward"]
softmax_backward = softmax_namespace["softmax_backward"]
bn_namespace = load_card("neural-networks/ml101-batchnorm-backward.md")
BatchNorm = bn_namespace["BatchNorm1D"]
bn_backward = bn_namespace["batchnorm_backward"]
conv_namespace = load_card("neural-networks/ml101-conv-backward.md")
conv = conv_namespace["conv2d_forward"]
conv_backward = conv_namespace["conv2d_backward"]
Optimizer = load_card("optimization/ml101-optimizer-implementation.md")["ArrayOptimizer"]
stump_namespace = load_card("ensemble/ml101-decision-stump-implementation.md")
best_stump = stump_namespace["best_stump"]
stump_predict = stump_namespace["stump_predict"]
PCA = load_card("unsupervised/ml101-pca-implementation.md")["SmallPCA"]


class KNNTests(unittest.TestCase):
    def test_examples_and_both_tie_rules(self):
        self.assertEqual(knn([[0], [2], [3]], [0, 1, 1], [1.8], 2), 1)
        self.assertEqual(knn([[0], [2]], [1, 0], [1], 1), 1)
        self.assertEqual(knn([[0], [2]], [1, 0], [1], 2), 0)
        self.assertEqual(knn([[0], [0], [5]], [2, 2, 0], [0], 3), 2)
        self.assertEqual(knn([[1, 0], [0, 2]], [8, 9], [0, 0], 1), 8)

    def test_validation_and_overflow(self):
        cases = [([], [], [1], 1), ([[0]], [], [0], 1),
                 ([[0]], [1], [0], 0), ([[0]], [1], [0], 2),
                 ([[0]], [1], [0], True), ([[0]], [1], [0], 1.5),
                 ([[0, 1]], [1], [0], 1), ([[]], [1], [], 1),
                 ([[math.nan]], [1], [0], 1), ([[0]], [1], [math.inf], 1),
                 ([[1e308]], [1], [-1e308], 1),
                 ([[1e200]], [1], [0.0], 1)]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                knn(*args)

    def test_translation_scaling_and_coordinate_permutation(self):
        rng = random.Random(20261022)
        for _ in range(100):
            X = [[rng.uniform(-5, 5) for _ in range(3)] for _ in range(15)]
            labels = [rng.randrange(3) for _ in X]
            q = [rng.uniform(-5, 5) for _ in range(3)]
            expected = knn(X, labels, q, 5)
            shifted = [[v * 3 + 7 for v in row] for row in X]
            self.assertEqual(knn(shifted, labels, [v * 3 + 7 for v in q], 5), expected)
            self.assertEqual(knn([row[::-1] for row in X], labels, q[::-1], 5), expected)


class BigramTests(unittest.TestCase):
    def test_documented_counts_and_probabilities(self):
        model = Bigram([["i", "like", "tea"], ["i", "like", "tea"],
                        ["i", "like", "coffee"]])
        self.assertEqual(model.predict("like"), "tea")
        self.assertAlmostEqual(model.probability("like", "tea"), 2 / 3)
        self.assertAlmostEqual(model.probability("like", "coffee"), 1 / 3)
        self.assertEqual(model.probability("like", "milk"), 0)
        self.assertIsNone(model.probability("tea", "i"))

    def test_boundaries_empty_unknown_and_tie(self):
        model = Bigram([[], ["solo"], ["a", "b"], ["c", "d"]])
        self.assertEqual(model.predict("a"), "b")
        for word in ["b", "d", "solo", "unknown"]:
            self.assertIsNone(model.predict(word))
        self.assertEqual(model.probability("a", "c"), 0)
        self.assertIsNone(Bigram([]).predict("anything"))
        self.assertEqual(Bigram([["x", "z"], ["x", "a"]]).predict("x"), "a")
        repeated = Bigram([["x", "x", "x"]])
        self.assertEqual(repeated.counts["x"]["x"], 2)
        self.assertEqual(repeated.probability("x", "x"), 1)

    def test_corpus_order_and_repetition_invariance(self):
        rng = random.Random(11)
        corpus = [[rng.choice("abcd") for _ in range(rng.randrange(8))]
                  for _ in range(100)]
        original = Bigram(corpus)
        repeated = Bigram(corpus * 3)
        rng.shuffle(corpus)
        shuffled = Bigram(corpus)
        for word in "abcd":
            self.assertEqual(original.predict(word), repeated.predict(word))
            self.assertEqual(original.predict(word), shuffled.predict(word))
            self.assertAlmostEqual(sum(original.probability(word, v) for v in "abcd"), 1)
            for following in "abcd":
                self.assertAlmostEqual(original.probability(word, following),
                                       repeated.probability(word, following))
                self.assertEqual(original.probability(word, following),
                                 shuffled.probability(word, following))


class KMeansTests(unittest.TestCase):
    def test_known_solution_and_objective(self):
        result = kmeans([[0], [2], [8], [10]], 2, init=[[0], [10]])
        np.testing.assert_allclose(result["centers"], [[1], [9]])
        np.testing.assert_array_equal(result["labels"], [0, 0, 1, 1])
        self.assertAlmostEqual(result["inertia"], 4)
        self.assertTrue(np.all(np.diff(result["history"]) <= 1e-12))

    def test_empty_clusters_and_final_assignment(self):
        result = kmeans([[1], [1], [1]], 3, init=[[1], [1], [1]])
        np.testing.assert_allclose(result["centers"], 1)
        np.testing.assert_array_equal(result["labels"], [0, 0, 0])
        X = np.array([[0], [2], [8], [10]])
        capped = kmeans(X, 2, init=[[0], [2]], max_iter=1)
        expected = ((X[:, None, :] - capped["centers"]) ** 2).sum(axis=2).argmin(axis=1)
        np.testing.assert_array_equal(capped["labels"], expected)
        self.assertEqual(capped["n_iter"], 1)

    def test_seed_invariance_and_invalid_inputs(self):
        X = np.array([[0, 0], [1, 1], [8, 8], [9, 9]], dtype=float)
        a = kmeans(X, 2, init=X[[0, 3]])
        b = kmeans(X * 3 + 5, 2, init=X[[0, 3]] * 3 + 5)
        np.testing.assert_array_equal(a["labels"], b["labels"])
        np.testing.assert_allclose(b["centers"], a["centers"] * 3 + 5)
        self.assertAlmostEqual(b["inertia"], a["inertia"] * 9)
        np.testing.assert_allclose(kmeans(X, 2, seed=7)["centers"],
                                   kmeans(X, 2, seed=7)["centers"])
        for kwargs in [{"k": 0}, {"k": 5}, {"k": True}, {"k": 2, "tol": -1},
                       {"k": 2, "max_iter": 0}, {"k": 2, "init": [[0]]}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                kmeans(X, **kwargs)


class NGramTests(unittest.TestCase):
    def test_counts_boundaries_backoff_and_unigram(self):
        model = NGramLM(3).fit([["i", "like", "tea"]] * 2 + [["i", "like", "coffee"]])
        self.assertEqual(model.next_counts(["i", "like"]), {"tea": 2, "coffee": 1})
        self.assertEqual(model.next_counts(["unknown", "like"]), {"tea": 2, "coffee": 1})
        boundary = NGramLM(2).fit([["a", "b"], ["c", "d"]])
        self.assertEqual(boundary.next_counts(["b"]), {"<EOS>": 1})
        self.assertNotIn("<BOS>", boundary.next_counts(["unknown"]))
        unigram = NGramLM(1).fit([["a", "b"], ["a"]])
        self.assertEqual(unigram.next_counts([]), {"a": 2, "b": 1, "<EOS>": 2})

    def test_sampling_and_reproducibility(self):
        model = NGramLM(2).fit([["x", "a"]] * 3 + [["x", "b"]])
        draws = [model.generate(prefix=["x"], max_tokens=1, seed=i)[0] for i in range(4000)]
        self.assertLess(abs(draws.count("a") / len(draws) - 0.75), 0.03)
        self.assertEqual(model.generate(seed=17), model.generate(seed=17))
        self.assertLessEqual(len(model.generate(max_tokens=2)), 2)
        self.assertEqual(model.generate(max_tokens=0), [])
        self.assertEqual(NGramLM(3).fit([[]]).generate(), [])

    def test_empty_and_reserved_inputs(self):
        with self.assertRaises(ValueError):
            NGramLM(0)
        with self.assertRaises(ValueError):
            NGramLM(2).fit([]).generate()
        with self.assertRaises(ValueError):
            NGramLM(2).fit([["<EOS>"]])
        with self.assertRaises(ValueError):
            NGramLM(2).fit([["a"]]).generate(max_tokens=-1)


class WordPieceTests(unittest.TestCase):
    def test_longest_match_and_whole_word_unknown(self):
        vocab = {"[UNK]", "play", "##ing", "p", "##lay"}
        self.assertEqual(wordpiece("playing", vocab), ["play", "##ing"])
        self.assertEqual(wordpiece("playx", vocab), ["[UNK]"])
        self.assertEqual(wordpiece("play", vocab), ["play"])
        self.assertEqual(wordpiece("", vocab), [])
        self.assertEqual(wordpiece("playing", vocab, max_chars=4), ["[UNK]"])
        self.assertEqual(wordpiece("abc", {"[UNK]", "ab", "a", "##bc"}), ["[UNK]"])

    def test_initial_continuation_and_reconstruction(self):
        self.assertEqual(wordpiece("ing", {"[UNK]", "##ing"}), ["[UNK]"])
        vocab = {"[UNK]", "a", "##a", "##b"}
        for word in ["a", "aa", "aab", "abab"]:
            pieces = wordpiece(word, vocab)
            self.assertEqual(pieces[0] + "".join(p[2:] for p in pieces[1:]), word)
        with self.assertRaises(ValueError):
            wordpiece("a", {"a"})


class EMTests(unittest.TestCase):
    def test_hand_calculation_and_probability_invariants(self):
        result = em_step([0, 2], [0.5, 0.5], [0, 2], [1, 1])
        r = 1 / (1 + math.exp(-2))
        np.testing.assert_allclose(result["responsibility"], [[r, 1-r], [1-r, r]])
        np.testing.assert_allclose(result["means"], [2*(1-r), 2*r])
        np.testing.assert_allclose(result["variances"], [4*r*(1-r)] * 2)
        np.testing.assert_allclose(result["weights"], [0.5, 0.5])
        self.assertGreaterEqual(result["loglik_after"], result["loglik_before"] - 1e-12)

    def test_repeated_updates_and_permutation(self):
        x = np.array([-3, -2, -1, 3, 4, 5], dtype=float)
        w, m, v = np.array([.4, .6]), np.array([-1., 2.]), np.array([2., 3.])
        for _ in range(12):
            result = em_step(x, w, m, v)
            self.assertGreaterEqual(result["loglik_after"], result["loglik_before"] - 1e-9)
            np.testing.assert_allclose(result["responsibility"].sum(axis=1), 1)
            mirrored = em_step(x, w[::-1], m[::-1], v[::-1])
            np.testing.assert_allclose(result["means"], mirrored["means"][::-1])
            w, m, v = [result[key] for key in ("weights", "means", "variances")]

    def test_floor_and_invalid_parameters(self):
        result = em_step([1, 1], [1], [0], [1])
        self.assertAlmostEqual(result["variances"][0], 1e-6)
        for args in [([], [1], [0], [1]), ([1], [0], [0], [1]),
                     ([1], [1], [0], [0]), ([1], [.5, .5], [0], [1, 1])]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                em_step(*args)


class BackpropTests(unittest.TestCase):
    def fixture(self):
        rng = np.random.default_rng(7)
        X = rng.normal(size=(3, 2)) * .2
        params = {"W1": rng.normal(size=(2, 3)) * .2,
                  "b1": np.array([.7, -.7, .9]),
                  "W2": rng.normal(size=(3, 2)) * .2,
                  "b2": np.array([.1, -.2])}
        return X, np.array([0, 1, 0]), params

    def test_hand_example_and_update(self):
        params = {"W1": np.array([[1.]]), "b1": np.array([0.]),
                  "W2": np.array([[0., 0.]]), "b2": np.array([0., 0.])}
        loss, grad = mlp([[2]], [0], params)
        self.assertAlmostEqual(loss, math.log(2))
        np.testing.assert_allclose(grad["W2"], [[-1, 1]])
        np.testing.assert_allclose(grad["b2"], [-.5, .5])
        np.testing.assert_allclose(grad["W1"], 0)
        _, updated = train_step([[2]], [0], params, .1)
        self.assertLess(mlp([[2]], [0], updated)[0], loss)
        np.testing.assert_allclose(params["W2"], 0)

    def test_all_parameter_and_input_gradients_by_central_difference(self):
        X, y, params = self.fixture()
        self.assertGreater(np.abs(X @ params["W1"] + params["b1"]).min(), .1)
        _, gradients = mlp(X, y, params)
        epsilon = 1e-5
        for key, array in [*params.items(), ("X", X)]:
            self.assertEqual(gradients[key].shape, array.shape)
            for index in np.ndindex(array.shape):
                original = array[index]
                array[index] = original + epsilon
                high = mlp(X, y, params)[0]
                array[index] = original - epsilon
                low = mlp(X, y, params)[0]
                array[index] = original
                numeric = (high - low) / (2 * epsilon)
                self.assertAlmostEqual(gradients[key][index], numeric, delta=2e-8,
                                       msg=f"{key}{index}")

    def test_batch_mean_broadcast_and_logit_stability(self):
        X, y, params = self.fixture()
        loss, grad = mlp(X, y, params)
        duplicated_loss, duplicated_grad = mlp(np.tile(X, (2, 1)), np.tile(y, 2), params)
        self.assertAlmostEqual(loss, duplicated_loss)
        for key in params:
            np.testing.assert_allclose(grad[key], duplicated_grad[key])
        shifted = {key: value.copy() for key, value in params.items()}
        shifted["b2"] += 1000
        self.assertAlmostEqual(mlp(X, y, shifted)[0], loss)
        shifted["b2"] = np.array([1000., -1000.])
        extreme_loss, extreme_grad = mlp(X, y, shifted)
        self.assertTrue(math.isfinite(extreme_loss))
        self.assertTrue(all(np.isfinite(v).all() for v in extreme_grad.values()))

    def test_zero_relu_derivative_and_invalid_labels(self):
        X, y, params = self.fixture()
        params["W1"][:] = 0
        params["b1"][:] = 0
        _, grad = mlp(X, y, params)
        np.testing.assert_allclose(grad["W1"], 0)
        np.testing.assert_allclose(grad["b1"], 0)
        with self.assertRaises(ValueError):
            mlp(X, [0, 2, 0], params)
        with self.assertRaises(ValueError):
            mlp(X, [0., 1., 0.], params)


def central_difference(array, objective, epsilon=1e-5):
    result = np.zeros_like(array, dtype=float)
    for index in np.ndindex(array.shape):
        original = array[index]
        try:
            array[index] = original + epsilon
            high = objective()
            array[index] = original - epsilon
            low = objective()
        finally:
            array[index] = original
        result[index] = (high - low) / (2 * epsilon)
    return result


class SoftmaxBackwardTests(unittest.TestCase):
    def test_arbitrary_upstream_numerical_gradient(self):
        rng = np.random.default_rng(12)
        z, g = rng.normal(size=(2, 4)), rng.normal(size=(2, 4))
        analytic = softmax_backward(g, softmax(z))
        numerical = central_difference(z, lambda: np.sum(softmax(z) * g))
        np.testing.assert_allclose(analytic, numerical, atol=1e-9, rtol=1e-7)
        np.testing.assert_allclose(analytic.sum(axis=1), 0, atol=1e-15)

    def test_example_constant_upstream_and_stability(self):
        p = softmax([[0, 0]])
        np.testing.assert_allclose(softmax_backward([[2, 0]], p), [[.5, -.5]])
        np.testing.assert_allclose(softmax_backward([[1, 1]], p), 0)
        np.testing.assert_allclose(softmax([[1000, 1001]]), softmax([[0, 1]]))
        np.testing.assert_allclose(softmax_backward([[7]], softmax([[42]])), 0)

    def test_invalid_shape_and_probabilities(self):
        with self.assertRaises(ValueError):
            softmax([])
        with self.assertRaises(ValueError):
            softmax_backward([[1, 2]], [[1]])
        with self.assertRaises(ValueError):
            softmax_backward([[1, 2]], [[.5, .8]])


class BatchNormBackwardTests(unittest.TestCase):
    def test_input_scale_and_shift_gradients(self):
        rng = np.random.default_rng(13)
        X, g = rng.normal(size=(4, 3)), rng.normal(size=(4, 3))
        layer = BatchNorm(3, eps=1e-4)
        layer.gamma = np.array([.5, -1.2, 2.])
        layer.beta = np.array([.2, .4, -.1])
        _, cache = layer.forward(X)
        dx, dgamma, dbeta = bn_backward(g, cache)
        objective = lambda: np.sum(layer.forward(X)[0] * g)
        for value, expected in [(X, dx), (layer.gamma, dgamma), (layer.beta, dbeta)]:
            numeric = central_difference(value, objective)
            np.testing.assert_allclose(expected, numeric, atol=2e-9, rtol=1e-6)
        np.testing.assert_allclose(dx.sum(axis=0), 0, atol=1e-14)

    def test_running_update_and_inference_independence(self):
        layer = BatchNorm(1, momentum=.5, eps=1e-5)
        result, _ = layer.forward([[1], [3]])
        np.testing.assert_allclose(result[:, 0], [-1, 1], atol=1e-5)
        np.testing.assert_allclose(layer.running_mean, [1])
        np.testing.assert_allclose(layer.running_var, [1])
        before = layer.running_mean.copy()
        alone, cache = layer.forward([[4]], training=False)
        combined, _ = layer.forward([[4], [100]], training=False)
        np.testing.assert_allclose(alone[0], combined[0])
        np.testing.assert_array_equal(layer.running_mean, before)
        with self.assertRaises(ValueError):
            bn_backward([[1]], cache)

    def test_singleton_constant_and_shape_errors(self):
        layer = BatchNorm(2)
        output, cache = layer.forward([[4, 8]])
        dx, dgamma, dbeta = bn_backward([[2, 3]], cache)
        np.testing.assert_allclose(output, 0)
        np.testing.assert_allclose(dx, 0)
        np.testing.assert_allclose(dgamma, 0)
        np.testing.assert_allclose(dbeta, [2, 3])
        with self.assertRaises(ValueError):
            layer.forward([[1]])


class ConvolutionBackwardTests(unittest.TestCase):
    def test_hand_example_overlap_and_zero_padding_crop(self):
        X = np.arange(1, 10, dtype=float).reshape(1, 1, 3, 3)
        K = np.array([[[[1., 0.], [0., -1.]]]])
        out, cache = conv(X, K, [0])
        np.testing.assert_allclose(out, -4)
        dx, dk, db = conv_backward(np.ones_like(out), cache)
        np.testing.assert_allclose(dk, [[[[12, 16], [24, 28]]]])
        np.testing.assert_allclose(dx, [[[[1, 1, 0], [1, 0, -1], [0, -1, -1]]]])
        np.testing.assert_allclose(db, [4])
        self.assertEqual(dx.shape, X.shape)

    def test_all_gradients_multichannel_stride_and_padding(self):
        rng = np.random.default_rng(14)
        X, K, b = rng.normal(size=(1, 2, 4, 5)), rng.normal(size=(2, 2, 2, 3)), rng.normal(size=2)
        out, cache = conv(X, K, b, stride=2, padding=1)
        g = rng.normal(size=out.shape)
        gradients = conv_backward(g, cache)
        objective = lambda: np.sum(conv(X, K, b, stride=2, padding=1)[0] * g)
        for value, analytic in zip((X, K, b), gradients):
            numerical = central_difference(value, objective)
            np.testing.assert_allclose(analytic, numerical, atol=2e-9, rtol=1e-6)

    def test_floor_output_shape_batch_sum_and_invalid_inputs(self):
        X = np.ones((2, 1, 4, 4))
        K = np.ones((1, 1, 3, 3))
        out, cache = conv(X, K, [0], stride=2)
        self.assertEqual(out.shape, (2, 1, 1, 1))
        _, dk, db = conv_backward(np.ones_like(out), cache)
        np.testing.assert_allclose(dk, 2)
        np.testing.assert_allclose(db, [2])
        with self.assertRaises(ValueError):
            conv(X, K, [0], stride=0)
        with self.assertRaises(ValueError):
            conv_backward(np.ones((1,)), cache)


class OptimizerImplementationTests(unittest.TestCase):
    def test_sgd_and_momentum_two_steps(self):
        for mode, expected in [("sgd", .6), ("momentum", .42)]:
            opt = Optimizer(mode, lr=.1, momentum=.9)
            value = np.array([1.])
            for _ in range(2):
                value = opt.step(value, [2])
            np.testing.assert_allclose(value, [expected])
            self.assertEqual(opt.t, 2)

    def test_adam_state_bias_correction_with_changing_sign(self):
        opt = Optimizer("adam", lr=.1, beta1=.5, beta2=.75, eps=.01)
        original = np.array([1.])
        first = opt.step(original, [2])
        expected_first = 1 - .1 * 2 / (2 + .01)
        np.testing.assert_allclose(first, [expected_first])
        second = opt.step(first, [-2])
        # m1=1, v1=1; m2=-.5, v2=1.75; corrected moments are -2/3 and 4.
        expected_second = expected_first + .1 * (2/3) / (2 + .01)
        np.testing.assert_allclose(second, [expected_second])
        np.testing.assert_allclose(opt.m, [-.5])
        np.testing.assert_allclose(opt.v, [1.75])
        np.testing.assert_allclose(original, [1])
        self.assertEqual(opt.t, 2)
        constant = Optimizer("adam", lr=.1)
        value = constant.step([1], [2])
        value = constant.step(value, [2])
        np.testing.assert_allclose(value, [.8], atol=2e-9)

    def test_zero_gradient_and_state_shape(self):
        for mode in ("sgd", "momentum", "adam"):
            opt = Optimizer(mode)
            np.testing.assert_allclose(opt.step([1, 2], [0, 0]), [1, 2])
            with self.assertRaises(ValueError):
                opt.step([1], [1])
        with self.assertRaises(ValueError):
            Optimizer(beta1=1)


class DecisionStumpTests(unittest.TestCase):
    def test_known_best_threshold_and_both_impurities(self):
        X, y = [[0], [1], [2], [3]], [0, 0, 1, 1]
        for criterion, gain in [("gini", .5), ("entropy", 1.)]:
            model = best_stump(X, y, criterion=criterion)
            self.assertEqual(model["feature"], 0)
            self.assertEqual(model["threshold"], 1.5)
            self.assertAlmostEqual(model["gain"], gain)
            np.testing.assert_array_equal(stump_predict(X, model), y)

    def test_feature_tie_pure_constant_and_min_leaf(self):
        model = best_stump([[0, 0], [1, 1], [2, 2], [3, 3]], [0, 0, 1, 1])
        self.assertEqual(model["feature"], 0)
        for X, y, kwargs, expected in [([[1], [1]], [2, 1], {}, 1),
                                       ([[0], [1]], [3, 3], {}, 3),
                                       ([[0], [1], [2]], [0, 1, 1], {"min_leaf": 2}, 1)]:
            leaf = best_stump(X, y, **kwargs)
            self.assertIsNone(leaf["feature"])
            np.testing.assert_array_equal(stump_predict(X, leaf), expected)

    def test_multiclass_duplicates_and_permuted_samples(self):
        X, y = np.array([[0], [0], [1], [2], [2]]), np.array([0, 0, 1, 2, 2])
        original = best_stump(X, y)
        shuffled = best_stump(X[::-1], y[::-1])
        self.assertEqual(original, shuffled)
        self.assertGreater(original["gain"], 0)
        with self.assertRaises(ValueError):
            best_stump([[math.nan]], [0])


class PCAImplementationTests(unittest.TestCase):
    def test_rank_one_example_and_training_mean(self):
        X = np.array([[-1., -1.], [0., 0.], [1., 1.]])
        model = PCA().fit(X, 1)
        np.testing.assert_allclose(model.inverse_transform(model.transform(X)), X, atol=1e-14)
        np.testing.assert_allclose(model.explained_variance, [2])
        np.testing.assert_allclose(model.explained_variance_ratio, [1])
        projected = model.transform([[10, 10]])
        self.assertGreater(abs(projected[0, 0]), 10)
        np.testing.assert_allclose(model.components @ model.components.T, [[1]])

    def test_reconstruction_error_discarded_spectrum_and_translation(self):
        rng = np.random.default_rng(15)
        X = rng.normal(size=(8, 4))
        errors = []
        for k in range(1, 5):
            model = PCA().fit(X, k)
            error = np.sum((X - model.inverse_transform(model.transform(X))) ** 2)
            self.assertAlmostEqual(error, np.sum(model.singular_values[k:] ** 2), places=11)
            errors.append(error)
        self.assertTrue(np.all(np.diff(errors) <= 1e-11))
        self.assertLess(errors[-1], 1e-24)
        base, shifted = PCA().fit(X, 2), PCA().fit(X + 9, 2)
        np.testing.assert_allclose(base.components.T @ base.components,
                                   shifted.components.T @ shifted.components, atol=1e-13)

    def test_constant_data_and_invalid_dimensions(self):
        X = np.ones((3, 2))
        model = PCA().fit(X, 2)
        np.testing.assert_allclose(model.explained_variance_ratio, 0)
        np.testing.assert_allclose(model.inverse_transform(model.transform(X)), X)
        with self.assertRaises(ValueError):
            PCA().fit([[1, 2]], 1)
        with self.assertRaises(ValueError):
            PCA().fit(X, 3)
        with self.assertRaises(ValueError):
            model.transform([[1]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
