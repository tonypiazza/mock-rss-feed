# app/domains/social.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_HANDLES = ["@ada", "@grace", "@alan", "@linus", "@margaret"]
_POSTS = [
    "Just shipped something I'm proud of!", "Hot take: tabs > spaces.",
    "Coffee count today: 4 and rising.", "TIL something delightful.",
    "Anyone else seeing this? #curious",
]


@register
class SocialDomain(DomainGenerator):
    domain_key = "social"
    default_params = {"hashtags": ["#tech", "#life", "#news"]}
    param_schema = {"hashtags": list}
    default_categories = ["trending", "reply", "repost", "mention", "like"]

    def make_item(self, ts, params, categories, rng):
        handle = rng.choice(_HANDLES)
        post = rng.choice(_POSTS)
        tag = rng.choice(params["hashtags"])
        return FeedItem(
            guid=f"{self.domain_key}-{ts.isoformat()}",
            title=f"{handle}: {post[:40]}",
            summary=f"{post} {tag}",
            published=ts,
            categories=categories,
            link_suffix=handle.lstrip("@"),
        )
