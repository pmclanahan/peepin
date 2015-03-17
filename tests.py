import os
from shutil import rmtree
from tempfile import mkdtemp, gettempdir
from contextlib import contextmanager
from unittest import TestCase
from functools import wraps
from glob import glob

import httpretty

import peepin


@contextmanager
def tmpfile(name='requirements.txt'):
    dir_ = mkdtemp('peepintest')
    try:
        yield os.path.join(dir_, name)
    finally:
        rmtree(dir_)


def cleanup_tmpdir(pattern):

    def decorator(test):
        @wraps(test)
        def inner(self, *args, **kwargs):
            try:
                return test(self, *args, **kwargs)
            finally:
                for each in glob(os.path.join(gettempdir(), pattern)):
                    os.remove(each)
        return inner
    return decorator


class Tests(TestCase):

    @httpretty.activate
    def test_get_latest_version_simple(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/peepin",
            body="""
            <div id="content">

            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin">peepin</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin/0.3">0.3</a>
            </div>
            """,
        )

        version = peepin.get_latest_version('peepin')
        self.assertEqual(version, '0.3')

    @httpretty.activate
    def test_get_hashes_error(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/somepackage/1.2.3",
            body="""
            <div id="content">

            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin">peepin</a>

            </div>
            """,
        )

        self.assertRaises(
            peepin.PackageError,
            peepin.run,
            'somepackage==1.2.3',
            'doesntmatter.txt'
        )

    @httpretty.activate
    def test_get_latest_version_multiversion(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/django",
            body="""
            <div id="content">
            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>
                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/Django">Django</a>
            </div>
            ...
            <div class="section">
              <h1>Index of Packages</h1>

            <table class="list">
            <tr>
             <th>Package</th>

             <th>Description</th>
            </tr>

            <tr class="odd">
             <td><a href="/pypi/Django/1.7.x">Django&nbsp;1.7.x</a></td>

             <td>A high-level Python Web framework that ...
            </tr>
            <tr class="even">
             <td><a href="/pypi/Django/1.7">Django&nbsp;1.7</a></td>

             <td>A high-level Python Web framework that ...
            </tr>
            <tr class="odd">
             <td><a href="/pypi/Django/1.6.8">Django&nbsp;1.6.8</a></td>

            """,
        )

        version = peepin.get_latest_version('django')
        self.assertEqual(version, '1.7.x')

    def test_amend_requirements_content_new(self):
        requirements = """
# empty so far
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, requirements + new_lines)

    def test_amend_requirements_content_replacement(self):
        requirements = """
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, new_lines)

    def test_amend_requirements_content_replacement_2(self):
        requirements = """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, new_lines)

    def test_amend_requirements_content_replacement_amonst_others(self):
        previous = """
# sha256: cHay6ATFKumO3svU3B-8qBMYb-f1_dYlR4OgClWntEI
otherpackage==1.0.0
""".strip() + '\n'
        requirements = previous + """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, previous + new_lines)

    def test_amend_requirements_content_replacement_amonst_others_2(self):
        previous = """
# sha256: 6nj05rvk7z_4OHM6mUIsl7GjE2plb4N3PqnJWaSRRlw
https://github.com/rhelmer/pyinotify/archive/9ff352f.zip#egg=pyinotify
""".strip() + '\n'
        requirements = previous + """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, previous + new_lines)

    @httpretty.activate
    @cleanup_tmpdir('peepin*')
    def test_run(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/peepin",
            body="""
            <div id="content">

            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin">peepin</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin/0.3">0.3</a>
            </div>
            """,
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/peepin/0.10",
            # sorry
            body="""
<a href="https://pypi.python.org/packages/2.7/p/peepin/peepin-0.10-py2-none-any.whl#md5=0a"
    >peepin-0.10-py2-none-any.whl</a>

<a href="https://pypi.python.org/packages/3.3/p/peepin/peepin-0.10-py3-none-any.whl#md5=45"
    >peepin-0.10-py3-none-any.whl</a>

<a href="https://pypi.python.org/packages/source/p/peepin/peepin-0.10.tar.gz#md5=ae"
    >peepin-0.10.tar.gz</a>
            """,
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/packages/2.7/p/peepin/peepin-0.10-py2-none-any.whl#md5=0a",
            body="Some py2 wheel content\n",
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/packages/3.3/p/peepin/peepin-0.10-py3-none-any.whl#md5=45",
            body="Some py3 wheel content\n",
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/packages/source/p/peepin/peepin-0.10.tar.gz#md5=ae",
            body="Some tarball content\n",
        )
        with tmpfile() as filename:
            open(filename, 'w').write('')
            retcode = peepin.run('peepin==0.10', filename)
            self.assertEqual(retcode, 0)
            output = open(filename).read()
            lines = output.splitlines()

            self.assertEqual(lines[0], '')
            self.assertEqual(lines[1], '# sha256: MRBPjA-YFqbSE120Iyz6JIssdSVZYmMhZXfTzck6PCU')
            self.assertEqual(lines[2], '# sha256: YftZIx_-lnzmk6IJnP9ZomlebQKsu2sFEDPjsRB9gAg')
            self.assertEqual(lines[3], '# sha256: svBtPE0Ui2SHaKurUIavrAQU5J60gT4fPEULl1x3zuk')
            self.assertEqual(lines[4], 'peepin==0.10')
