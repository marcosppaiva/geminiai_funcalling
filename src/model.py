import uuid
from dataclasses import dataclass, field


@dataclass
class Product:
    """ """

    _id: str = field(init=False, default_factory=lambda: str(uuid.uuid4()))
    sku: str
    name: str
    description: str
    in_stock: bool
