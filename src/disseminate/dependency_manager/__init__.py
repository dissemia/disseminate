"""
Dependency managers keep track of which files a document needs to create and
render a specific target format. It will convert or modify the dependencies as
needed.

A dependency manager's responsibilities are:

1. *Manage dependencies*. A dependency comprises a dependency path (the path
   of the source file), a destination pate (the path of the file to create in
   the rendered target. Additionally, each dependency can reconstruct a URL for
   the dependency, relative to the target directory.
2. *Search files*. The dependency manager is responsible for checking the
   dependency (source) file path using the 'paths' entry in the context.
   If a dependency is not found, an exception (:exc:`MissingDependency
   <disseminate.dependency_manager.dependency_manager.MissingDependency>`)
   is raised.
3. *Convert files*. If a rendered target requires a dependency with a different
   format, the dependency manager will use converters
   (:obj:`disseminate.converters`) to convert the file.
"""

from .dependency_manager import (DependencyManager, MissingDependency,
                                 FileDependency)
