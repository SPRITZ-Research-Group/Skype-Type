from dst.libraries.dictionary_filter import dictionary_interactive

def console(in_queue, config):
    for s_line in config.SPLASHSCREEN:
        print(s_line)
    output = []
    for idx, pred in iter(in_queue.get, None):
        output.append((idx,pred))
    output.sort(key = lambda k: k[0]);
    print("PREDICTIONS")
    print("")
    for i, p in output:
        print("{} - {}".format(i, p))
    dictionary_interactive([y for (x,y) in output], config)

    
    
