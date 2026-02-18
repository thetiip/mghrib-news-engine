"""Spider implementations package."""
from .base import BaseSpider
from .hespress import HespressSpider
from .medias24 import Medias24Spider

__all__ = ['BaseSpider', 'HespressSpider', 'Medias24Spider']
