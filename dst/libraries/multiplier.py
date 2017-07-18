def multiplier(in_queue, out_queues):
    for res in iter(in_queue.get, None):
        for out in out_queues:
            out.put(res)
