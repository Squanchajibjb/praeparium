from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal

class ProductSpec(BaseModel):
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    certifications: List[str] = []
    key_claims: List[str] = []
    claim_evidence: List[str] = []
    price_usd: Optional[float] = None
    affiliate_urls: List[HttpUrl] = []
    pros: List[str] = []
    cons: List[str] = []
    best_for: List[str] = []

class Persona(BaseModel):
    code: Literal["URBAN","ELDERLY","FAMILY","HOMESTEAD","BUGOUT","APARTMENT","RURAL","COASTAL"]
    pain_points: List[str]
    triggers: List[str]
    constraints: List[str]

class CategoryCore(BaseModel):
    seed_concept: str
    primary_keyword: str
    timeframe_ladder: List[str]
    market_context: str

class ArticlePlan(BaseModel):
    article_id: str
    article_type: Literal["HUB","GUIDE","REVIEW","ROUNDUP","FAQ"]
    title: str
    slug: str
    primary_keyword: str
    template: Literal["hub.md.j2","guide.md.j2","review.md.j2","roundup.md.j2","faq.md.j2"]
    personas: List[str] = []
    dependencies: List[str] = []
    priority: int = 100
    evidence_requirements: List[str] = []
    interlink_out: List[str] = []
    taxonomy: List[str] = []

class ArticleHarness(BaseModel):
    slug: str
    meta_description: str
    title_hint: Optional[str] = None
    voice_profile: Literal["Wirecutter-meets-Cosmo","Neutral-Gov","Conversational"] = "Conversational"
    ctas: List[str] = []
    disclaimer: Optional[str] = None
    author_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    last_reviewed_iso: Optional[str] = None

class SOP1Bundle(BaseModel):
    category: CategoryCore
    personas: List[Persona]
    products: List[ProductSpec] = []
    narrative_hooks: List[str] = []
    harness: ArticleHarness
    article_plan: List[ArticlePlan]
