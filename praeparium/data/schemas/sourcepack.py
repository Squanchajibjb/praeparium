# praeparium/data/schemas/sourcepack.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class SourceRef(BaseModel):
    id: str
    title: str
    url: HttpUrl
    publisher: Optional[str] = None
    accessed: Optional[str] = None

class Product(BaseModel):
    name: str
    brand: Optional[str] = None
    capacity_l: Optional[float] = None
    material: Optional[str] = None
    certifications: List[str] = []
    stackable: Optional[bool] = None
    footprint: Optional[str] = None
    price_usd: Optional[float] = None
    affiliate_urls: List[HttpUrl] = []

class ArticlePlan(BaseModel):
    article_id: str
    type: str             # "HUB" | "REVIEW" | "GUIDE" | ...
    slug: str
    require_comparison_table: bool = False

class SourcePack(BaseModel):
    pack_id: str
    domain: str
    version: str
    title: str
    slug: str
    sources: List[SourceRef]
    claims_checklist: List[str]
    products: List[Product] = []
    comparison_columns: List[str] = []
    articles: List[ArticlePlan] = []
