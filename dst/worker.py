from sklearn.externals import joblib


def worker(pipeline, in_queue, out_queue, n_preds, config):
    clf = joblib.load(pipeline.name)
    for idx, sample in iter(in_queue.get, None):
        if idx < 0:
            break
        prediction = clf.predict_proba(sample.reshape(1, -1))[0]
        values = [x[0] for x in
                  sorted([(clf.classes_[x], val) for x, val in enumerate(prediction) if val != 0.0],
                         key=lambda _x: _x[1], reverse=True)]
        out_queue.put((idx, values[:n_preds]))
    return
