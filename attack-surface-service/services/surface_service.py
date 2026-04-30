from typing import List, Dict
from urllib.parse import urljoin
from collections import defaultdict
from surface.parameter_mapper import ParameterMapper
from surface.context_identifier import ContextIdentifier
from utils.logger import get_logger

logger = get_logger("SurfaceService")

class SurfaceService:

    @staticmethod
    def build_attack_surface(crawler_output) -> List[Dict]:
        surface_map = defaultdict(set)

        try:
            pages = [crawler_output] if isinstance(crawler_output, dict) else crawler_output
            
            for page in pages:
                # If passed as Pydantic models, use .url; if dict, use .get()
                url = getattr(page, "url", page.get("url") if isinstance(page, dict) else None)
                if not url or any(url.endswith(ext) for ext in ['.jpg', '.png', '.pdf', '.css', '.js']):
                    continue

                forms = getattr(page, "forms", page.get("forms", []) if isinstance(page, dict) else [])

                # Process Query parameters from URL
                query_params = ParameterMapper.extract_from_url(url)
                for param in query_params:
                    surface_map[(url, "GET")].add(param)

                # Process Form parameters
                for form in forms:
                    # Handle both Pydantic objects and dicts
                    if not isinstance(form, dict):
                        form_dict = form.model_dump()
                    else:
                        form_dict = form
                        
                    form_params = ParameterMapper.extract_from_forms([form_dict])
                    method = form_dict.get("method", "POST").upper()
                    
                    # Resolve relative action URLs
                    action = form_dict.get("action")
                    target_url = urljoin(url, action) if action else url
                    
                    for param in form_params:
                        surface_map[(target_url, method)].add(param)

            # Convert the grouped map into a list of dictionaries matching AttackPoint schema
            attack_surface = [
                {
                    "url": url,
                    "method": method,
                    "parameters": sorted(list(params))
                } for (url, method), params in surface_map.items()
            ]

            logger.info(f"Built {len(attack_surface)} attack objects")

            return attack_surface

        except Exception as e:
            logger.error(f"Surface build failure: {e}")
            return []