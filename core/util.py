def humanize_n_bytes(n_bytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while n_bytes >= 1024 and i < len(suffixes)-1:
        n_bytes /= 1024.
        i += 1
    f = ('%.2f' % n_bytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
