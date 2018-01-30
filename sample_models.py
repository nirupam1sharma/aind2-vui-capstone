from keras import backend as K
from keras.models import Model
from keras.layers import (BatchNormalization, Conv1D, Conv2D, Dense, Input, 
    TimeDistributed, Activation, Bidirectional, SimpleRNN, GRU, GRU)

def simple_rnn_model(input_dim, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(output_dim,
                   return_sequences=True, 
                   implementation=2,
                   name='rnn')(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(simp_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def rnn_model(input_dim, units, activation, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(units,
                   activation=activation,
                   return_sequences=True,
                   implementation=2,
                   name='rnn')(input_data)
    # Add batch normalization - use default parameters
    bn_rnn = BatchNormalization()(simp_rnn)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model


def cnn_rnn_model(input_dim, filters, kernel_size, conv_stride,
    conv_border_mode, units, output_dim=29):
    """ Build a recurrent + convolutional network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add convolutional layer
    conv_1d = Conv1D(filters, kernel_size, 
                     strides=conv_stride, 
                     padding=conv_border_mode,
                     activation='relu',
                     name='conv1d')(input_data)
    # Add batch normalization
    bn_cnn = BatchNormalization(name='bn_conv_1d')(conv_1d)
    # Add a recurrent layer
    simp_rnn = GRU(units, activation='relu',
        return_sequences=True, implementation=2, name='rnn')(bn_cnn)
    # Add batch normalization - use default parameters
    bn_rnn = BatchNormalization()(simp_rnn)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: cnn_output_length(
        x, kernel_size, conv_border_mode, conv_stride)
    print(model.summary())
    return model

def cnn_output_length(input_length, filter_size, border_mode, stride,
                      dilation=1):
    """ Compute the length of the output sequence after 1D convolution along
        time. Note that this function is in line with the function used in
        Convolution1D class from Keras.
    Params:
        input_length (int): Length of the input sequence.
        filter_size (int): Width of the convolution kernel.
        border_mode (str): Only support `same` or `valid`.
        stride (int): Stride size used in 1D convolution.
        dilation (int)
    """
    if input_length is None:
        return None
    assert border_mode in {'same', 'valid'}
    dilated_filter_size = filter_size + (filter_size - 1) * (dilation - 1)
    if border_mode == 'same':
        output_length = input_length
    elif border_mode == 'valid':
        output_length = input_length - dilated_filter_size + 1
    return (output_length + stride - 1) // stride

def deep_rnn_model(input_dim, units, recur_layers, output_dim=29):
    """ Build a deep recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    last_rnn_out = input_data
    # Add recurrent layers and batch norms
    for i in range(recur_layers):
        simp_rnn = GRU(units,
                       activation='relu',
                       return_sequences=True,
                       implementation=2,
                       name='rnn_{}'.format(i + 1))(last_rnn_out)
        # Add batch normalization 1
        bn_rnn = BatchNormalization()(simp_rnn)
        last_rnn_out = bn_rnn
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(last_rnn_out)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def bidirectional_rnn_model(input_dim, units, output_dim=29):
    """ Build a bidirectional recurrent network for speech
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add bidirectional recurrent layer
    bidir_rnn = Bidirectional(
        GRU(units,
            activation='relu',
            return_sequences=True,
            implementation=2,
            name='rnn'))(input_data)
    # Add batch normalization 1
    bn_rnn = BatchNormalization()(bidir_rnn)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def final_model(input_dim, units, bidirectional=False, recur_layers=3, activation='relu',\
                dropout=0.0, recurrent_dropout=0.0, output_dim=29):
    """ Build a deep network for speech 
    """
     # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))

    # Add recurrent bidirectional layers
    last_rnn_out = input_data
    for i in range(recur_layers):
        if bidirectional:
            simpl_rnn = Bidirectional(
                GRU(units,
                    activation=activation,
                    return_sequences=True,
                    implementation=2,
                    name='rnn_{}'.format(i),
                    dropout=dropout,
                    recurrent_dropout=recurrent_dropout))(last_rnn_out)
        else:
            simpl_rnn = GRU(units,
                            activation=activation,
                            return_sequences=True,
                            implementation=2,
                            name='rnn_{}'.format(i),
                            dropout=dropout,
                            recurrent_dropout=recurrent_dropout)(last_rnn_out)
        # Add batch normalization
        bn_rnn = BatchNormalization()(simpl_rnn)
        last_rnn_out = bn_rnn

    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(last_rnn_out)

    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)

    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())

    return model