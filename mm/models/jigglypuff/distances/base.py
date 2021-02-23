from abc import ABC
import tensorflow as tf
import numpy as np

import pipelines.evaluate.query_by_example.model as m


class Base(m.Model, ABC):
    def __init__(self, export_dir: str):
        self.session = tf.Session(graph=tf.Graph())
        tf.saved_model.loader.load(self.session, ["serve"], export_dir)
        self.graph = self.session.graph

        self.input = self.graph.get_tensor_by_name("input:0")
        self.labels = self.graph.get_tensor_by_name("labels:0")
        self.output = self.graph.get_tensor_by_name("output:0")
        self.output_shape = self.graph.get_tensor_by_name("output_shape:0")
        self.logits = self.graph.get_tensor_by_name("logits:0")
        self.logits_shape = self.graph.get_tensor_by_name("logits_shape:0")
        self.log_prob = self.graph.get_tensor_by_name("log_prob:0")

        print(self.log_prob, self.labels)

    def get_output(self, audio: np.ndarray):
        output, shape = self.session.run((self.output, self.output_shape), feed_dict={
            self.input: audio
        })

        if output.ndim == 0:
            return np.array([output]), [1]

        return output, shape

    def get_logits(self, audio: np.ndarray):
        logits, shape = self.session.run((self.logits, self.logits_shape), feed_dict={
            self.input: audio
        })

        if logits.ndim == 0:
            return np.array([logits]), [1]

        return logits, shape

    def get_log_prob(self, audio: np.ndarray, labels: np.ndarray):
        return self.session.run((self.log_prob), feed_dict={
            self.input: audio,
            self.labels: labels
        })

    def __del__(self):
        """Cleanup tensorflow session on destruction of this object."""
        self.session.close()
