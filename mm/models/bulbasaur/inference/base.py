from abc import ABC
import tensorflow as tf
import numpy as np

import pipelines.evaluate.query_by_example.model as m


class Base(m.Model, ABC):
    def __init__(self, export_dir: str):
        self.session = tf.Session(graph=tf.Graph())
        tf.saved_model.loader.load(self.session, ["serve"], export_dir)
        self.graph = self.session.graph

        self.base_audio = self.graph.get_tensor_by_name("audio:0")
        self.base_embeddings = self.graph.get_tensor_by_name("embeddings:0")

        self.base_project = self.graph.get_tensor_by_name("project:0")
        self.base_project_shape = self.graph.get_tensor_by_name("project_shape:0")

        self.base_output = self.graph.get_tensor_by_name("output:0")
        self.base_output_shape = self.graph.get_tensor_by_name("output_shape:0")

        self.base_min_distance = self.graph.get_tensor_by_name("min_distance:0")
        self.base_distances = self.graph.get_tensor_by_name("distances:0")

    def get_projection(self, audio: np.ndarray):
        projection, shape = self.session.run((self.base_project, self.base_project_shape), feed_dict={
            self.base_audio: audio,
        })

        return projection, shape

    def get_output(self, embeddings: np.ndarray, audio: np.ndarray):
        output, min_distance = self.session.run((self.base_output, self.base_min_distance), feed_dict={
            self.base_audio: audio,
            self.base_embeddings: embeddings
        })

        return output, min_distance

    def get_distances(self, embeddings: np.ndarray, audio: np.ndarray):
        return self.session.run(self.base_distances, feed_dict={
            self.base_audio: audio,
            self.base_embeddings: embeddings
        })

    def __del__(self):
        """Cleanup tensorflow session on destruction of this object."""
        self.session.close()
