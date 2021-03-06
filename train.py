import tensorflow as tf

from model import generator_model, discriminator_model
from reader import reader
"""
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="1"
"""
from tensorflow.python.client import device_lib
print device_lib.list_local_devices()

reader = reader('data/small/weibo_pair_train_Q.post',
    'data/small/weibo_pair_train_Q.response', 'data/words.txt')

print len(reader.d)

g_model = generator_model(vocab_size=len(reader.d),
    embedding_size=128,
    lstm_size=128,
    num_layer=4,
    max_length_encoder=40,
    max_length_decoder=40,
    max_gradient_norm=2,
    batch_size_num=20,
    learning_rate=0.001,
    beam_width=5)
d_model = discriminator_model(vocab_size=len(reader.d),
    embedding_size=128,
    lstm_size=128,
    num_layer=4,
    max_post_length=40,
    max_resp_length=40,
    max_gradient_norm=2,
    batch_size_num=20,
    learning_rate=0.001)

saver = tf.train.Saver(tf.global_variables(), keep_checkpoint_every_n_hours=1.0)

sess = tf.Session()
try:
    loader = tf.train.import_meta_graph('saved/model.ckpt.meta')
    loader.restore(sess, tf.train.latest_checkpoint('saved/'))
    print 'load finished'
except:
    sess.run(tf.global_variables_initializer())
    print 'load failed'

d_step = 5
g_step = 50
loop_num = 0

try:
    
    for _ in range(10000):
        g_model.pretrain(sess, reader)
    
    for _ in range(100):
        d_model.update(sess, g_model, reader)
    
    while True:
        for _ in range(d_step):
            g_model.update(sess, d_model, reader)
        for _ in range(g_step):
            d_model.update(sess, g_model, reader)
        loop_num += 1
        if loop_num % 50 == 0:
            saver.save(sess, 'saved/model.ckpt')
except KeyboardInterrupt:
    saver.save(sess, 'saved/model.ckpt')
