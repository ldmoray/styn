import contextlib
import imp
import pytest
import re
import sys

if sys.version.startswith("3."):
    from io import StringIO as SOut
else:
    from StringIO import StringIO as SOut

from os import path
from styn import _styn, main


def fpath(mod):
    return path.splitext(mod.__file__)[0] + '.py'


def simulate_dynamic_module_load(mod):
    file_path = fpath(mod)
    dynamically_loaded_mod = imp.load_source(path.splitext(path.basename(file_path))[0], file_path)
    return dynamically_loaded_mod


def reset_build_file(mod):
    mod.chores_run = []


def build(mod, params=None, init_mod=reset_build_file):
    dynamically_loaded_mod = simulate_dynamic_module_load(mod)
    dynamically_loaded_mod.chores_run = []
    sys.argv = ['styn', '-f', fpath(mod)] + (params or [])
    main()
    return dynamically_loaded_mod


class TestParseArgs:
    def test_parsing_commandline(self):
        args = _styn._create_parser().parse_args(['-f', "foo.py", "chore1", "chore2"])
        assert "foo.py" == args.file
        assert not args.list_chores
        assert ['chore1', 'chore2'] == args.chores

    def test_parsing_commandline_help(self):
        assert _styn._create_parser().parse_args(["-l"]).list_chores
        assert _styn._create_parser().parse_args(["--list-chores"]).list_chores

    def test_parsing_commandline_build_file(self):
        assert "some_file" == _styn._create_parser().parse_args(["-f", "some_file"]).file
        assert "build.py" == _styn._create_parser().parse_args([]).file
        assert "/foo/bar" == _styn._create_parser().parse_args(["--file", "/foo/bar"]).file

        with pytest.raises(SystemExit):
            _styn._create_parser().parse_args(["--file"])
        with pytest.raises(SystemExit):
            _styn._create_parser().parse_args(["-f"])


class TestBuildSimple:
    def test_get_chores(self):
        from .build_scripts import simple
        ts = _styn._get_chores(simple)
        assert len(ts) == 5


class TestBuildWithDependencies:
    def test_get_chores(self):
        from .build_scripts import dependencies
        chores = _styn._get_chores(dependencies)
        assert len(chores) == 5
        assert 3 == len([chore for chore in chores if chore.name == 'android'][0].dependencies)
        assert 3 == len([chore for chore in chores if chore.name == 'ios'][0].dependencies)

    def test_dependencies_for_imported(self):
        from .build_scripts import default_chore_and_import_dependencies
        chores = _styn._get_chores(default_chore_and_import_dependencies)
        assert 7 == len(chores)
        assert [chore for chore in chores if chore.name == 'clean']
        assert [chore for chore in chores if chore.name == 'local_chore']
        assert [chore for chore in chores if chore.name == 'android']
        assert 3 == len([chore for chore in chores if chore.name == 'chore_with_imported_dependencies'][0].dependencies)

    def test_dependencies_that_are_imported_e2e(self):
        from .build_scripts import default_chore_and_import_dependencies

        def mod_init(mod):
            mod.chores_run = []
            mod.build_with_params.chores_run = []

        module = build(default_chore_and_import_dependencies, ["chore_with_imported_dependencies"], init_mod=mod_init)
        assert module.chores_run == ['local_chore', 'chore_with_imported_dependencies']
        assert module.build_with_params.chores_run == ['clean[/tmp]', 'html']


class TestDecorationValidation:
    def test_chore_without_braces(self):
        with pytest.raises(Exception) as exc:
            from .build_scripts import annotation_misuse_1
        assert 'Replace use of @chore with @chore().' in str(exc.value)

    def test_dependency_not_a_chore(self):
        with pytest.raises(Exception) as exc:
            from .build_scripts import annotation_misuse_2
        assert re.findall('function html.* is not a chore.', str(exc.value))

    def test_dependency_not_a_function(self):
        with pytest.raises(Exception) as exc:
            from .build_scripts import annotation_misuse_3
        assert '1234 is not a chore.' in str(exc.value)


@contextlib.contextmanager
def mock_stdout():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [SOut(), SOut()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


class TestOptions:
    @pytest.fixture
    def module(self):
        from .build_scripts import options as module
        self.docs = {'clean': '', 'html': 'Generate HTML.',
                     'images': '''Prepare images.\n\nShould be ignored.''',
                     'android': 'Package Android app.'}
        return module

    def test_ignore_chores(self, module):
        module = build(module, ["android"])
        assert ['clean', 'html', 'android'] == module.chores_run

    def test_docs(self, module):
        chores = _styn._get_chores(module)
        assert 4 == len(chores)

        for chore_ in chores:
            assert chore_.name in self.docs
            assert self.docs[chore_.name] == chore_.doc

    @pytest.mark.parametrize('args', [['-l'], ['--list-chores'], []])
    def test_list_docs(self, module, args):
        with mock_stdout() as out:
            build(module, args)
        stdout = out[0]
        chores = _styn._get_chores(module)
        for chore in chores:
            if chore.ignored:
                assert re.findall('%s\s+%s\s+%s' % (chore.name, "\[Ignored\]", chore.doc), stdout)
            else:
                assert re.findall('%s\s+%s' % (chore.name, chore.doc), stdout)


class TestRuntimeError:
    def test_stop_on_exception(self):
        from .build_scripts import runtime_error as rerr
        with pytest.raises(IOError):
            build(rerr, ["android"])
        mod = simulate_dynamic_module_load(rerr)
        assert mod.ran_images
        assert not hasattr(mod, 'ran_android')

    def test_exception_on_invalid_chore_name(self):
        from .build_scripts import build_with_params
        with pytest.raises(Exception) as exc:
            build(build_with_params, ["doesnt_exist"])

            assert 'chore should be one of append_to_file, clean' \
                   ', copy_file, echo, html, start_server, tests' in str(exc.value)


class TestPartialChoreNames:
    def setup_method(self, method):
        from .build_scripts import build_with_params
        self._mod = build_with_params

    def test_with_partial_name(self):
        mod = build(self._mod, ["cl"])
        assert ['clean[/tmp]'] == mod.chores_run

    def test_with_partial_name_and_dependencies(self):
        mod = build(self._mod, ["htm"])
        assert ['clean[/tmp]', 'html'] == mod.chores_run

    def test_exception_on_conflicting_partial_names(self):
        with pytest.raises(Exception) as exc:
            build(self._mod, ["c"])
        assert ('Conflicting matches clean, copy_file for chore c' in str(exc.value) or
                'Conflicting matches copy_file, clean for chore c' in str(exc.value))


class TestDefaultChore:
    def test_simple_default_chore(self):
        from .build_scripts import simple
        assert _styn._run_default_chore(simple)  # returns false if no default chore

    def test_module_with_defaults_which_imports_other_files_with_defaults(self):
        from .build_scripts import default_chore_and_import_dependencies
        mod = build(default_chore_and_import_dependencies)
        assert 'chore_with_imported_dependencies' in mod.chores_run


class TestMultipleChores:
    def setup_method(self, method):
        from .build_scripts import build_with_params
        self._mod = build_with_params

    def test_dependency_is_run_only_once_unless_explicitly_invoked_again(self):
        mod = build(self._mod, ["clean", "html", 'tests', "clean"])
        assert ['clean[/tmp]', "html", "tests[]", "clean[/tmp]"] == mod.chores_run

    def test_multiple_partial_names(self):
        assert ['clean[/tmp]', "html"] == build(self._mod, ["cl", "htm"]).chores_run


class TestChoreArguments:
    def setup_method(self, method):
        from .build_scripts import build_with_params
        self._mod = build_with_params
        self._mod.chores_run = []

    def test_passing_optional_params_with_dependencies(self):
        mod = build(self._mod, ["clean[~/project/foo]",
                                'append_to_file[/foo/bar,ABCDEF]',
                                "copy_file[/foo/bar,/foo/blah,False]",
                                'start_server[8080]'])
        assert ["clean[~/project/foo]", 'append_to_file[/foo/bar,ABCDEF]',
                "copy_file[/foo/bar,/foo/blah,False]", 'start_server[8080,True]'
                ] == mod.chores_run

    def test_invoking_varargs_chore(self):
        mod = build(self._mod, ['tests[test1,test2,test3]'])
        assert ['tests[test1,test2,test3]'] == mod.chores_run

    def test_partial_name_with_args(self):
        mod = build(self._mod, ['co[foo,bar]', 'star'])
        assert ['clean[/tmp]', 'copy_file[foo,bar,True]', 'start_server[80,True]'] == mod.chores_run

    def test_passing_keyword_args(self):
        mod = build(self._mod, ['co[to=bar,from_=foo]', 'star[80,debug=False]', 'echo[foo=bar,blah=123]'])

        assert ['clean[/tmp]', 'copy_file[foo,bar,True]',
                'start_server[80,False]',
                'echo[blah=123,foo=bar]'] == mod.chores_run

    def test_passing_varargs_and_keyword_args(self):
        assert (['echo[1,2,3,some_str,111=333,bar=123.3,foo=xyz]'] ==
                build(self._mod, ['echo[1,2,3,some_str,111=333,foo=xyz,bar=123.3]']).chores_run)

    def test_validate_keyword_arguments_always_after_args(self):
        with pytest.raises(Exception) as exc:
            build(self._mod, ['echo[bar=123.3,foo]'])
        assert "Non keyword arg foo cannot follows a keyword arg bar=123.3" in str(exc.value)

        with pytest.raises(Exception) as exc:
            build(self._mod, ['copy[from_=/foo,/foo1]'])
        assert "Non keyword arg /foo1 cannot follows" \
               " a keyword arg from_=/foo" in str(exc.value)

    def test_invalid_number_of_args(self):
        with pytest.raises(TypeError) as exc:
            build(self._mod, ['append[1,2,3]'])
        print(str(exc.value))
        assert re.findall('takes .*2 .*arguments', str(exc.value))

    def test_invalid_names_for_kwargs(self):
        with pytest.raises(TypeError) as exc:
            build(self._mod, ['copy[1=2,to=bar]'])
        assert "got an unexpected keyword argument '1'" in str(exc.value)

        with pytest.raises(TypeError) as exc:
            build(self._mod, ['copy[bar123=2]'])
        assert "got an unexpected keyword argument 'bar123'" in str(exc.value)
