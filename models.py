"""
Model definitions for the campaign automation pipeline
"""
from dataclasses import dataclass
from typing import List


@dataclass
class CampaignBrief:
    """Represents a campaign brief for social ad campaign"""
    product_name: str
    target_region_market: str
    target_audience: str
    campaign_message: str
    
    def to_dict(self):
        return {
            "product_name": self.product_name,
            "target_region_market": self.target_region_market,
            "target_audience": self.target_audience,
            "campaign_message": self.campaign_message
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            product_name=data["product_name"],
            target_region_market=data["target_region_market"],
            target_audience=data["target_audience"],
            campaign_message=data["campaign_message"]
        )

