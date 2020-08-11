import tensorflow as tf

# for encoding a log we need:
# the vocab, i.e. the activity space -> a python list of the events
# the number of oov_buckets, lets say 2 for now
# creating a lookup table with the indices for each possible activity
# functions that encode a trace, i.e. a sequence of events into an one_hot vector, embedding respectively -> getting traces as python lists as input

class log_encoder():

    def __init__(self, activity_list, num_oov_bucktes, embedding_dim=None):
        self.activities = activity_list
        self.num_oov_buckets = num_oov_bucktes

        self.indices = tf.range(len(self.activities), dtype=tf.int64)
        self.table_init = tf.lookup.KeyValueTensorInitializer(self.activities, self.indices)
        self.table = tf.lookup.StaticVocabularyTable(self.table_init, self.num_oov_buckets)

        #only needed for embeddings
        if embedding_dim:
            embed_init = tf.random.uniform([len(self.activities)+self.num_oov_buckets, embedding_dim])
            self.embedding_matrix = tf.Variable(embed_init)

    def lookup_indices(self, trace):
        categories = tf.constant(trace)
        cat_indices = self.table.lookup(categories)
        return cat_indices

    def one_hot_encode_trace(self, trace):
        cat_indices = self.lookup_indices(trace)
        cat_one_hot = tf.one_hot(cat_indices, depth=len(self.activities) + self.num_oov_buckets)
        return cat_one_hot

    def one_hot_encode_log(self, log):
        #log is not in the format as when loaded with pm4py, but rather a list(=log) of lists(=traces) containing the activities as strings
        encoded_inputs = []
        for trace in log:
            encoded_inputs.append(self.one_hot_encode_trace(trace))
        
        return encoded_inputs

    def embed_encode_trace(self, trace):
        cat_indices = self.lookup_indices(trace)
        cat_embed = tf.nn.embedding_lookup(self.embedding_matrix, cat_indices)
        return cat_embed

    def embed_encode_log(self, log):
        #log is not in the format as when loaded with pm4py, but rather a list(=log) of lists(=traces) containing the activities as strings
        encoded_inputs = []
        for trace in log:
            encoded_inputs.append(self.embed_encode_trace(trace))
        
        return encoded_inputs