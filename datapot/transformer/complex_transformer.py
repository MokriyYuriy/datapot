from __future__ import division

from .base_transformer import BaseTransformer

CONFIDENCE_PENALTY = 0.1
CONFIDENCE_REWARD = 0.1


class TestComplexTransformer(BaseTransformer):
    """Transform array of ints to normalized sum

    Transform array of ints to their sum
    divided on average length of array in training set
    """

    @staticmethod
    def requires_fit():
        return True

    def __str__(self):
        return 'TestComplexTransformer(average_len_of_array={})'.format(self.average_len_of_array)

    def __repr__(self):
        return self.__str__()

    def __init__(self):
        self.average_len_of_array = None

    def validate(self, field, value):
        # check that value is list
        if not isinstance(value, list):
            self.confidence = max(self.confidence - CONFIDENCE_PENALTY, 0)
            return False

        # ignore fields which name ends with 'xy' or 'log
        # well, just because we can
        if field[-2::] == 'xy' or field[-3::] == 'log':
            self.confidence = max(self.confidence - CONFIDENCE_PENALTY, 0)
            return False

        # check that list contains only ints
        for obj in value:
            if not isinstance(obj, int):
                self.confidence = max(self.confidence - CONFIDENCE_PENALTY, 0)
                return False

        self.confidence = min(self.confidence + CONFIDENCE_REWARD, 1)
        return True

    def fit(self, all_values):
        # let's count average length of array here
        # actually it doesn't make any sense but who cares
        self.average_len_of_array = sum([len(x) for x in all_values if x is not None]) / len(all_values)

    def names(self):
        return 'sum'

    def transform(self, value):
        if self.average_len_of_array is None:
            raise Exception('Attempt to transform non-fitted transformer')
        if value is None:
            return None
        return sum(value) / self.average_len_of_array
