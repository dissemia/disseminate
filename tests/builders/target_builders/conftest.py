import pytest

from disseminate.paths import SourcePath


@pytest.fixture
def setup_example(env, doc_cls):
    """Setup and example document"""
    def example(project_root, subpath):
        context = env.context
        tmpdir = context['target_root']
        src_filepath = SourcePath(project_root=project_root,
                                  subpath=subpath)

        doc = doc_cls(src_filepath=src_filepath, environment=env)
        env.context = doc.context
        return env, doc
    return example