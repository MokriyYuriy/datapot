from .base_transformer import  BaseTransformer
import sklearn
import collections

# TODO: change constant's name
CATEGORICAL_MAX_SIZE = 100

class BaseCategoricalTransformer(BaseTransformer):
    """
    Base class for categorical transformers
    """

    validate_set = set()
    repeats = 0
    _n_components = 0

    @staticmethod
    def requires_fit():
        return True

    def validate(self, field, value):

        if not isinstance(value, collections.Hashable):
            return

        if value in self.validate_set:
            self.repeats += 1
        else:
            self.validate_set.add(value)

        if float(self.repeats) / (len(self.validate_set) + self.repeats) >= 0.5:
            self.confidence = 1
        else:
            self.confidence = 0.6


class SVDOneHotTransformer(BaseCategoricalTransformer):
    """
    One-hot encoding with dimension reduction (SVD) in case there are too many features .
    """

    apply_dimension_reduction = False
    features = dict()

    def __init__(self, dimension_reduction=True):
        self.dimension_reduction = True

    def __str__(self):
        return "SVDOneHotTransformer"

    def names(self):
        return ['one_hot' + str(i) for i in range(self._n_components)]

    def fit(self, value):
        # TODO: what if value is not hashable
        self.features = dict()
        self.apply_dimension_reduction = False


        for x in value:
            if x not in self.features:
                self.features[x] = len(self.features)

        if len(self.features) <= CATEGORICAL_MAX_SIZE:
            self.one_hot_encoder = sklearn.preprocessing.OneHotEncoder(sparse=False,
                                                                       handle_unknown='ignore')
            self._n_components = len(self.features)
        else:
            self.apply_dimension_reduction = True
            self.one_hot_encoder = sklearn.preprocessing.OneHotEncoder(sparse=True,
                                                                       handle_unknown='ignore')
            self._n_components = 10

        self.one_hot_encoder.fit([[self.features[x]] for x in value])

        if self.apply_dimension_reduction:
            self.dim_reducer = sklearn.decomposition.TruncatedSVD(n_components=self._n_components)
            self.dim_reducer.fit(self.one_hot_encoder.transform([[self.features[x]] for x in value]))

        return self

    def transform(self, value):
        if not isinstance(value, collections.Hashable):
            return None
        value = [[self.features[value]]] if value in self.features else [[len(self.features)]]
        feature_array = self.one_hot_encoder.transform(value)
        if self.apply_dimension_reduction:
            return self.dim_reducer.transform(feature_array)[0].tolist()
        else:
            return feature_array[0].tolist()


class CountersTransformer(BaseCategoricalTransformer):
    """
    Counters transformer.
    """
    pass
