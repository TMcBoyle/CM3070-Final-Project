import tensorflow as tf
import numpy as np

from chess.board import Board
from chess.sides import Side

def bitboard_to_list(board: int):
    return np.reshape([int(x) for x in f"{board:064b}"], (8, 8))

def main():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Input(shape=(18, 8, 8)))
    model.add(tf.keras.layers.Convolution2D(32, (3, 3), activation="relu"))
    model.add(tf.keras.layers.Convolution2D(32, (3, 3), activation="relu"))
    model.add(tf.keras.layers.GlobalAveragePooling2D())
    model.add(tf.keras.layers.Dense(32, activation="relu"))
    model.add(tf.keras.layers.Dense(64, activation="sigmoid"))
    model.add(tf.keras.layers.Dense( 2, activation="softmax"))

    board = Board()

    data = []
    for b in board.pieces[Side.WHITE].values():
        data.append(bitboard_to_list(b))
    for b in board.pieces[Side.BLACK].values():
        data.append(bitboard_to_list(b))
    data.append(bitboard_to_list(board.white))
    data.append(bitboard_to_list(board.black))
    data.append(bitboard_to_list(board.duck))
    data.append(bitboard_to_list(board.occupied))
    data.append(bitboard_to_list(board.castle_rights))
    data.append(bitboard_to_list(board.en_passant))
    data = np.array(data)

    print(model.predict(np.expand_dims(data, 0))[0][0])

if __name__ == "__main__":
    main()
