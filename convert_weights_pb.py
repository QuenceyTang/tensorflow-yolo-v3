# -*- coding: utf-8 -*-

import numpy as np
import tensorflow as tf
import yolo_v3, dense_yolov3_v1
import yolo_v3_tiny
import yolov3_tiny_3l
from PIL import Image, ImageDraw

from utils import load_weights, load_names, detections_boxes, freeze_graph

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string(
    'class_names', 'bird.names', 'File with class names')
tf.app.flags.DEFINE_string(
    'weights_file', '/home/tk/Share/darknet/weights/yolov3-dense_final.weights', 'Binary file with detector weights')
tf.app.flags.DEFINE_string(
    'data_format', 'NHWC', 'Data format: NCHW (gpu only) / NHWC')
tf.app.flags.DEFINE_string(
    'output_graph', 'saved_model_pb/dense_yolo.pb', 'Frozen tensorflow protobuf model output path')

tf.app.flags.DEFINE_bool(
    'tiny', False, 'Use tiny version of YOLOv3')
tf.app.flags.DEFINE_bool(
    'dense', True, 'Use dense version of YOLOv3')
tf.app.flags.DEFINE_integer(
    'size', 608, 'Image size')


def main(argv=None):
    if FLAGS.tiny:
        model = yolov3_tiny_3l.yolo_v3_tiny
    elif FLAGS.dense:
        model = dense_yolov3_v1.dense_yolo_v3
    else:
        model = yolo_v3.yolo_v3

    classes = load_names(FLAGS.class_names)

    # placeholder for detector inputs
    inputs = tf.placeholder(tf.float32, [None, FLAGS.size, FLAGS.size, 3], "inputs")

    with tf.variable_scope('detector'):
        detections = model(inputs, len(classes), data_format=FLAGS.data_format)
        load_ops = load_weights(tf.global_variables(scope='detector'), FLAGS.weights_file)

    # Sets the output nodes in the current session
    boxes = detections_boxes(detections)

    with tf.Session() as sess:
        sess.run(load_ops)
        freeze_graph(sess, FLAGS.output_graph)
        writer = tf.summary.FileWriter("logs/", sess.graph)


if __name__ == '__main__':
    tf.app.run()
