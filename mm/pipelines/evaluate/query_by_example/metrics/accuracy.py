from pipelines.evaluate.query_by_example.metrics.metric import Metric

class Accuracy(Metric):
    def __init__(self, window: int):
        self.window = window

        self.per_class_correct = {}
        self.per_class_incorrect = {}

        self.per_class_fp = {}
        self.per_class_total = {}

        self.total = 0

    def update(self, pred_utterances: [str], pred_at_time: [int], utterances: [str], at_time: [int], total: int):
        """Updates per class accuracy for a new task.

        Given two sequences

        (hello, 1), (cool, 100), (well, 129)
        (hello, 10), (well, 128)

        and a window size

        a utterance is considered correct if there is a utterance of the same keyword in the labels within 'window'
        """

        # Total number of predictions made 'including None'
        self.total += total

        p_len = len(pred_utterances)
        l_len = len(utterances)

        p_got_match = [False] * p_len
        l_got_match = [False] * l_len

        for p in range(p_len):
            for l in range(l_len):
                matches = ((abs(pred_at_time[p] - at_time[l]) < self.window)
                           and (pred_utterances[p] == utterances[l]))

                p_got_match[p] |= matches
                l_got_match[l] |= matches

        for l in range(l_len):
            if utterances[l] not in self.per_class_correct:
                self.per_class_correct[utterances[l]] = 0

            if utterances[l] not in self.per_class_incorrect:
                self.per_class_incorrect[utterances[l]] = 0

            self.per_class_correct[utterances[l]] += l_got_match[l]
            self.per_class_incorrect[utterances[l]] += (1 - l_got_match[l])

        for p in range(p_len):
            if pred_utterances[p] not in self.per_class_fp:
                self.per_class_fp[pred_utterances[p]] = 0

            if pred_utterances[p] not in self.per_class_total:
                self.per_class_total[pred_utterances[p]] = 0

            self.per_class_fp[pred_utterances[p]] += (1 - p_got_match[p])
            self.per_class_total[pred_utterances[p]] += 1

    def summarize(self):
        for cl in self.per_class_total.keys():
            if cl in self.per_class_correct and cl in self.per_class_incorrect:
                print(
                    f"{cl} catch_rate {self.per_class_correct[cl]} / {(self.per_class_correct[cl] + self.per_class_incorrect[cl])} = {self.per_class_correct[cl] / (self.per_class_correct[cl] + self.per_class_incorrect[cl])}")

        for cl in self.per_class_total.keys():
            print(
                f"{cl} fp_rate {self.per_class_fp[cl]} / {(self.per_class_total[cl])} = {self.per_class_fp[cl] / (self.per_class_total[cl])}")
            print(
                f"{cl} tn_rate 1 - ({self.per_class_fp[cl]} / {self.total}) = {1 - (self.per_class_fp[cl] / self.total)}")
