import matplotlib.image as mpimg
import numpy as np
from random import randint
import os

NUM_PIXEL_CHANNELS = 512 * 512 * 3
NUM_CODE_CHANNELS = 737289  # (18 length-bits + 180kB) / 2 = 737289
CODE_BITS_PER_CHANNEL = 2
LENGTH_BITS = 18
LSB_MASK = np.asarray(3, dtype=np.uint8) # Int representation of '00000011'
MSB_MASK = np.invert(LSB_MASK)
demo_password = "Shoob"

def bin_to_int(arr, num_bits, dtype=None):
    """ Converts array of binary ints to int, or the given dtype.
    Allows for broadcasting (input should have array size (N,num_bits) """
    if len(arr.shape) > 1:
        assert arr.shape[1] == num_bits
    else:
        assert arr.shape[0] == num_bits
    return arr.dot(2**np.arange(num_bits, dtype=dtype)[::-1])


def preprocess_data(input_data):
    """ Preprocess the given binary input data (in (N, 8) numpy array)
    for encoding """
    num_bytes, _ = input_data.shape
    bin_rep = np.binary_repr(num_bytes)
    # Pad binary repr of num_bytes with '0's on the left to make it 18 bits
    bin_rep = (LENGTH_BITS - len(bin_rep)) * '0' + bin_rep
    # Convert to numpy array and add to data
    data_rep = np.array([int(x) for x in list(bin_rep)], dtype=np.uint8)
    # Append the length in front of our data to get full data string,
    # then convert to (N+18, 2) array
    full_data = np.append(data_rep, input_data).reshape((-1,2))

    # Convert the 2-bit arrays into uint8 and reshape back to 1D array
    return bin_to_int(full_data, CODE_BITS_PER_CHANNEL, dtype=np.uint8).reshape(-1)

def text_to_data(input_data, encoding='utf8'):
    """ Converts text data into (N,8) numpy array of bits"""
    # Convert to data to a list of bytes, represented as integers
    data_binary_stream = [int(x) for x in bytearray(input_data, encoding)]
    # Convert into numpy array of uint8 and convert to row vector
    data_arr = np.array(data_binary_stream, dtype=np.uint8)[:, np.newaxis]
    # Unpack each value into bits, yielding a (N,8) array of bits
    return np.unpackbits(data_arr, axis=1)


def generate_mask(password):
    """ Generate the mask (1D index array) using the given password as
    seed to the numpy pseudo-random number generator """
    np.random.seed(password_to_seed(password))
    return np.random.choice(NUM_PIXEL_CHANNELS, NUM_CODE_CHANNELS, replace=False)

def password_to_seed(password):
    """ Converts a string password to an array of uint32 based on
    bytes """
    # TODO: Each byte is only 8 bits, but we're converting each to a uint32.
    # Find a way to convert to actually uint32
    pw_bytes = [int(x) for x in bytearray(password, 'utf8')]
    return np.array(pw_bytes, dtype=np.uint32)

def encode_data(src_arr, data_arr):
    """ Encodes the data_arr elementwise onto src_arr 2-lsb.
    data_arr has to be same shape as src_arr """
    return np.bitwise_and(src_arr, MSB_MASK) + data_arr

def encrypt(src, data, password):
    """ Encode the processed data onto the source (image) array (now flattened
    to 1D array and return the encoded image.
    NOTE: data array is smaller than source array """
    # Replace the 2-LSB of every pixel-channel in the src image with random noise
    encoded = encode_data(src, np.random.randint(0, high=2**CODE_BITS_PER_CHANNEL, size=src.shape, dtype=np.uint8))

    # Get the 1D index array
    idx = generate_mask(password)[:data.size]

    # Encode the data onto the corresponding positions
    encoded[idx] = encode_data(encoded[idx], data)

    return encoded


def get_rand_img():
    val = randint(0, 2)
    if val == 0:
        return 'encode_red.png'
    elif val == 1:
        return 'encode_blue.png'
    else:
        return 'encode_green.png'


def encryption_api(str):
    """ Accepts a string from client, encrypts the string onto
    the image, and returns encrypted image """
    # Get image and store in img variable
    img_file = get_rand_img()
    img = load_image(os.path.join(os.getcwd(), 'templates', img_file))
    img = read_img_to_1D_arr(img)
    processed_data = preprocess_data(text_to_data(str))
    encrypted = encrypt(img, processed_data, demo_password)
    assert str == decrypt(encrypted, demo_password)
    # Convert back to img
    result = encrypted.reshape((512, 512, 3))
    assert str == decrypt(result.reshape(-1), demo_password)
    mpimg.imsave("res.png", result)
    return "res.png"

def read_img_to_1D_arr(img):
    img = (img * 255).round().astype(np.uint8)
    return img.flatten()

def decryption_api(encoded_img, password):
    """ Accepts as input an encoded image and password. Returns
    the plaintext """
    # Convert to flattened numpy array
    assert encoded_img.shape == (512,512,3)
    encoded_arr = read_img_to_1D_arr(encoded_img)
    return decrypt(encoded_arr, password)

def decrypt(encoded_arr, password):
    """ Decrypts the 1D encoded numpy array """
    assert(encoded_arr.shape == (NUM_PIXEL_CHANNELS,))
    # Get the indices of our data points
    idx = generate_mask(password)
    # Decode and return
    return decode_data(encoded_arr[idx])

def decode_data(encoded_data):
    """ Decode the filtered encoded data into string """
    # Recover the 2-lsb, then reshape into row vector
    data_arr = np.bitwise_and(encoded_data, LSB_MASK)[:, np.newaxis]
    length_2bits = data_arr[:LENGTH_BITS/2]
    data_2bits = data_arr[LENGTH_BITS/2:]
    # Unpack the length bits, extract the two-bits then reshape into 1D array
    length_2bits_inter = np.unpackbits(length_2bits, axis=1)[:,-2:].reshape(-1)
    # Retrieve the length (num-bytes)
    num_bytes = bin_to_int(length_2bits_inter, length_2bits_inter.size)
    # Unpack the data bits up to num_bytes, extract the two-bits then reshape into (N, 8) array
    data_8bits = np.unpackbits(data_2bits[:num_bytes*4], axis=1)[:, -2:].reshape(-1,8)
    assert data_8bits.shape == (num_bytes, 8)

    data_bytes = bin_to_int(data_8bits, 8, dtype=np.uint8)
    #return data_bytes.tostring().decode('utf-8')
    return data_bytes.tostring()
def load_image(filename):
    return mpimg.imread(filename)[:,:,:3]

def password_seed_test():
    assert np.array_equal(generate_mask(demo_password), generate_mask(demo_password))

def run_tests():
    password_seed_test()

# run_tests()
# encryption_api("HELLOWORLD")
#image = load_image("telegram/image.png")
#print(decryption_api(image, demo_password))
#assert(res == "HELLOWORLD")

