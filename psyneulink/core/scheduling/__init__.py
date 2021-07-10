"""
This module provides utilities used to schedule the execution of psyneulink components

https://princetonuniversity.github.io/PsyNeuLink/Scheduling.html
"""
import re

import graph_scheduler

from . import condition
from . import scheduler
from . import time

from .condition import *
from .scheduler import *
from .time import *

__all__ = list(condition.__all__)
__all__.extend(scheduler.__all__)
__all__.extend(time.__all__)


_documentation_mirror_note = """.. note::
\tThis documentation is mirrored from the `graph_scheduler <https://www.github.com/kmantel/graph-scheduler>`_ package and often refers to ``nodes``, ``edges`` , and ``graphs``. In PsyNeuLink terms, ``nodes`` are `Mechanism`\\ s or `Composition`\\ s, ``edges`` are `Projection`\\ s, and ``graphs`` are `Composition`\\ s. The one exception is during `learning <Composition_Learning>`, in which `Projection`\\ s may be assigned for execution as nodes to ensure that `MappingProjection`\\ s are updated in the proper order."""

_global_doc_subs = [
    (
        r'<graph_scheduler',
        '<psyneulink.core.scheduling'
    ),
]

# insert docstrings from graph_scheduler and perform replacements for
# psyneulink-specific terminology and links
for module in ['scheduler', 'condition', 'time']:
    ext_module = getattr(graph_scheduler, module)
    module = locals()[module]
    module.__doc__ = _documentation_mirror_note + ext_module.__doc__

    for pattern, repl in _global_doc_subs:
        for cls_name in [*module.__all__, module]:
            try:
                cls = getattr(module, cls_name)
            except TypeError:
                # is module
                cls = cls_name

            if cls.__doc__ is None:
                cls.__doc__ = f'{getattr(ext_module, cls_name).__doc__}'

            cls.__doc__ = re.sub(pattern, repl, cls.__doc__, flags=re.MULTILINE | re.DOTALL)

    for cls, repls in module._doc_subs.items():
        if cls is None:
            cls = module
        else:
            cls = getattr(module, cls)

        for pattern, repl in repls:
            cls.__doc__ = re.sub(pattern, repl, cls.__doc__, flags=re.MULTILINE | re.DOTALL)

del graph_scheduler
del re
