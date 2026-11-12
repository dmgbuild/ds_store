from importlib.metadata import version


def define_env(env):
    """Expose project metadata as variables for use in Markdown pages."""
    release = version("ds_store")
    env.variables["release"] = release
    env.variables["version"] = ".".join(release.split(".")[:2])
