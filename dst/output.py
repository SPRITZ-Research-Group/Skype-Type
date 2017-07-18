from dst.libraries.dictionary_filter import dictionary_interactive


def console(in_queue, config):
    for s_line in config.SPLASHSCREEN:
        print s_line
    output = []
    for idx, pred in iter(in_queue.get, None):
        output.append(pred)

    print "PREDICTIONS"
    print ""
    for i, p in enumerate(output):
        print "{} - {}".format(i, p)
    dictionary_interactive(output, config)
