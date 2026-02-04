from typing import List, Dict
import statistics


class PricingAgent:
    """Generates baseline, competitive, and premium pricing scenarios.
    Uses configurable rate cards and provides per-requirement breakdown and sensitivity analysis."""

    def __init__(self, rate_per_hour: float = 120.0, productivity_factor: float = 0.8):
        self.rate = rate_per_hour
        self.productivity = productivity_factor

    def _estimate_hours(self, text: str) -> int:
        words = len(text.split())
        # improved heuristic: base 40h + 10h per 100 words scaled by productivity
        base = 40
        extra = (words // 100) * 10
        hours = int((base + extra) * self.productivity)
        return max(8, hours)

    def estimate(self, requirements: List[Dict]) -> Dict:
        line_items = []
        hours_list = []
        for req in requirements:
            text = req.get('text', '')
            hours = self._estimate_hours(text)
            cost = round(hours * self.rate, 2)
            hours_list.append(hours)
            line_items.append({
                "requirement_id": req.get('id', ''),
                "hours": hours,
                "cost": cost,
                "notes": "Heuristic estimate; replace with historical ML model if available.",
            })

        total_hours = sum(hours_list)
        baseline = sum(item['cost'] for item in line_items)
        competitive = round(baseline * 0.92, 2)
        premium = round(baseline * 1.25, 2)

        sens_high = round(baseline * 1.15, 2)
        sens_low = round(baseline * 0.85, 2)

        return {
            "line_items": line_items,
            "total_hours": total_hours,
            "scenarios": {
                "baseline": baseline,
                "competitive": competitive,
                "premium": premium,
            },
            "sensitivity": {"-15%": sens_low, "+15%": sens_high},
            "rate_per_hour": self.rate,
        }
