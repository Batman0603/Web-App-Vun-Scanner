from typing import List, Dict
from surface.parameter_mapper import ParameterMapper
from surface.context_identifier import ContextIdentifier
from utils.logger import get_logger

logger = get_logger("SurfaceService")

class SurfaceService:

    @staticmethod
    def build_attack_surface(crawler_output) -> List[Dict]:
        from surface.attack_object import AttackObject

        attack_surface = []

        try:
            # Handle both single dict and list of dicts
            pages = [crawler_output] if isinstance(crawler_output, dict) else crawler_output
            
            for page in pages:

                url = page.get("url")
                forms = page.get("forms", [])

                if not url:
                    continue

                # Query parameters
                query_params = ParameterMapper.extract_from_url(url)
                for param in query_params:
                    attack_surface.append(
                        AttackObject(
                            url=url,
                            method="GET",
                            parameter=param,
                            context=ContextIdentifier.identify_from_url()
                        ).to_dict()
                    )

                # Form parameters
                for form in forms:
                    form_params = ParameterMapper.extract_from_forms([form])
                    context = ContextIdentifier.identify_from_form(form)
                    method = form.get("method", "POST").upper()

                    for param in form_params:
                        attack_surface.append(
                            AttackObject(
                                url=url,
                                method=method,
                                parameter=param,
                                context=context
                            ).to_dict()
                        )

            logger.info(f"Built {len(attack_surface)} attack objects")

            return attack_surface

        except Exception as e:
            logger.error(f"Surface build failure: {e}")
            return []