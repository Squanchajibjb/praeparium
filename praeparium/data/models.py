# praeparium/data/models.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class EditorialTargets(BaseModel):
    fk_max: float = 8.0
    style_min: float = 0.85
    min_quotes: int = 2
    min_stats: int = 2
    min_faqs: int = 5
    min_internal_links: int = 3
    min_external_links: int = 2
    min_words: int = 900
    min_sections: int = 6
    narrative_flow_required: bool = True
    reviewer_signoff_required: bool = True


class Author(BaseModel):
    author_id: str
    display_name: str
    bio: Optional[str] = None
    credentials: List[str] = Field(default_factory=list)
    expertise_domains: List[str] = Field(default_factory=list)


class ArticlePlan(BaseModel):
    slug: str
    title: str
    template: Optional[str] = None
    primary_keyword: Optional[str] = None
    personas: List[str] = Field(default_factory=list)
    interlink_out: List[str] = Field(default_factory=list)
    author_id: Optional[str] = None
    reviewer_id: Optional[str] = None


class Methodology(BaseModel):
    # Optional – placeholder if/when you add methodology files
    objectives_ref: Optional[str] = None
    requirements_ref: Optional[str] = None
    design_ref: Optional[str] = None
    deployment_ref: Optional[str] = None


class Bundle(BaseModel):
    bundle_slug: Optional[str] = None
    article_plan: List[ArticlePlan] = Field(default_factory=list)
    authors: List[Author] = Field(default_factory=list)
    editorial_targets: EditorialTargets = EditorialTargets()
    methodology: Optional[Methodology] = None
