import math

from nose.tools import raises

from collecting import google


@raises(ValueError)
def test_google_chunkify_error():
    ''' Check chunkify handles invalid chunk size. '''
    items = [i for i in range(42)]
    google.chunkify(items, 0)


def test_google_chunkify():
    ''' Check chunkify works as expected. '''
    p = 10
    for n in (1, 10, 42, 300):
        items = [i for i in range(n)]
        chunks = list(google.chunkify(items, p))
        # Check the number of chunks
        assert len(chunks) == math.ceil(n / p)
        # Check the length of each chunk
        for chunk in chunks[:-1]:
            assert len(chunk) == p
        # Check the size of the last chunk
        rest = n % p
        if rest != 0:
            assert len(chunks[-1]) == rest
        else:
            assert len(chunks[-1]) == p


def test_google_unchunkify():
    ''' Check unchunkify works as expected. '''
    for m in (1, 2, 3):
        for n in (1, 2, 3):
            # Generate sorted sublists of sorted values
            items = [
                [
                    m * n + j
                    for _ in range(n)
                ]
                for j in range(m)
            ]
            flat_list = google.unchunkify(items)
            # Check the length of flattened list
            assert len(flat_list) == m * n
            # Check the flattened list is sorted
            is_sorted = all(
                flat_list[i] <= flat_list[i+1]
                for i in range(len(flat_list)-1)
            )
            assert is_sorted is True


def test_google_googleify():
    ''' Check googleify works as expected. '''
    n = 30
    points = [
        {'latitude': 1, 'longitude': 1}
        for _ in range(n)
    ]
    locations = google.googleify(points)
    assert len(locations.split('|')) == n

