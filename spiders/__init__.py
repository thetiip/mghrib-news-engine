"""Spider implementations package."""
from .base import BaseSpider
from .hespress import HespressSpider
from .le360 import Le360Spider
from .medias24 import Medias24Spider
from .elbotola import ElbotolaSpider
from .telquel import TelQuelSpider
from .yabiladi import YabiladiSpider

__all__ = [
    'BaseSpider',
    'HespressSpider',
    'Le360Spider',
    'Medias24Spider',
    'ElbotolaSpider',
    'TelQuelSpider',
    'YabiladiSpider',
]
