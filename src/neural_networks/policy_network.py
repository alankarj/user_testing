import tensorflow as tf

STATE = 'state'
ACTION = 'action'
LR = 'learning_rate'
LAYER_SUFFIX = 'layer_'
OUTPUT_LAYER = 'output_layer'


class PolicyNetwork:
    def __init__(self, params):
        self.params = params

    def construct_network(self):
        params = self.params
        state = tf.placeholder(dtype=tf.float32, shape=[None, params.state_dim], name=STATE)
        action = tf.placeholder(dtype=tf.float32, shape=[None, params.action_dim], name=ACTION)
        learning_rate = tf.placeholder(dtype=tf.float32, shape=[None], name=LR)
        regularizer = tf.contrib.layers.l2_regularizer(params.lambda_reg)
        global_step = tf.Variable(0, trainable=False, name='global_step')

        h = state
        for i in range(params.num_hidden_layers):
            h = tf.layers.dense(h, params.hidden_dim, activation=tf.nn.relu, name=LAYER_SUFFIX + str(i),
                                kernel_initializer=tf.glorot_uniform_initializer(),
                                kernel_regularizer=regularizer, bias_regularizer=regularizer)
        action_pred = tf.layers.dense(h, params.hidden_dim, activation=tf.nn.relu, name=OUTPUT_LAYER,
                                      kernel_initializer=tf.glorot_uniform_initializer(),
                                      kernel_regularizer=regularizer, bias_regularizer=regularizer)

        loss = tf.losses.softmax_cross_entropy(action, action_pred)
        optimizer = tf.train.AdamOptimizer(learning_rate)
        train_op = optimizer.minimize(loss, global_step=global_step)