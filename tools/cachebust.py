from __future__ import unicode_literals, print_function

import re
import hashlib
import os
import sys
import glob

SCRIPT_RE = re.compile(r'data-main="/js/([a-z]+)"')
STYLE_RE = re.compile(r'href="/css/([a-z]+)\.css"')


def busted(path):
    """ Returns potentially busted versions of path """
    base, ext = os.path.splitext(path)
    return glob.glob('%s*%s' % (base, ext))


def rename_to_sha1(path):
    """ Renames a file to filename with SHA1 hash and returns hexdigest """
    path = os.path.normpath(path)
    b = busted(path)
    if b and b[0] != path:
        base, ext = os.path.splitext(path)
        return b[0][len(base) + 1:-len(ext)]
    f = open(path, 'r')
    s = f.read()
    f.close()
    sha1 = hashlib.sha1()
    sha1.update(s)
    h = sha1.hexdigest()[:6]
    basepath, ext = os.path.splitext(path)
    new_name = '%s-%s%s' % (basepath, h, ext)
    os.rename(path, new_name)
    return h


def has_ext(path, ext):
    """ Returns True if path has given extension """
    return os.path.splitext(path)[1] == ext


def in_dir(path, fn, exts=['.html'], debug=False):
    """ For given directory path, run function an all files recursively """
    for root, rirs, files in os.walk(path):
        if debug:
            print('Entering %s' % root)
        for name in files:
            if not any([has_ext(name, e) for e in exts]):
                continue
            if debug:
                print('Processing %s' % name)
            fn(os.path.join(root, name))


def get_replacer(base_path, ext=None):
    """ Returns a replacer function that is used with re.sub() calls """
    if not ext:
        ext = os.path.basename(base_path)  # Use directory name as extension
    def replacer(match):
        s = match.group(0)
        g = match.group(1)
        if not g:
            return
        path = '%s/%s.%s' % (base_path, g, ext)
        h = rename_to_sha1(path)
        return s.replace(g, '%s-%s' % (g, h))
    return replacer


script_replacer = get_replacer('build/static/js')
style_replacer = get_replacer('build/static/css')


def relink_file(path):
    """ Generic function that replinks assets in a file """
    f = open(path, 'r')
    content = f.read()
    f.close()
    new_content = SCRIPT_RE.sub(script_replacer, content)
    new_content = STYLE_RE.sub(style_replacer, new_content)
    if new_content == content:
        return
    f = open(path, 'w')
    f.write(new_content)
    f.close()


if __name__ == '__main__':
    in_dir(os.path.normpath(sys.argv[-1]), relink_file, debug=True)
