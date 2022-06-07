def tf_generator(tokens):
    vector = counter(tokens)
    for key, val in vector.items():
        tf = val / len(tokens)
        update = {key : tf}
        vector.update(update)
    return vector

def counter(tokens):
    tf = {}
    for w in tokens:
        if w in tf:
            tf[w] +=1
        else:
            tf[w] = 1
    return tf