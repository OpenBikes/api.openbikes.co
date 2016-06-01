from app import util


def test_util_slugify():
    ''' Check util.slugify works as expected. '''
    string = '-0 -- - ?XYz!-@'
    expected = '0-xyz'
    slug = util.slugify(string)
    assert slug == expected
