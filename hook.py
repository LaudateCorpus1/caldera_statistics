from aiohttp_jinja2 import template, web
from plugins.statistics.app.mitre_loader import tdds_from_url
# Based on the example in the documentation - which happens to already be very close to what I need for the initial version
# https://caldera.readthedocs.io/en/latest/How-to-Build-Plugins.html

# To compare it to the MITR Att@ck framework:
# https://github.com/mitre/cti
# https://stix2.readthedocs.io/en/latest/
# https://oasis-open.github.io/cti-documentation/

name = 'Statistics'
description = 'View statistics'
address = '/plugin/statistics/gui'


async def enable(services):
    app = services.get('app_svc').application
    fetcher = AbilityFetcher(services)
    app.router.add_route('*', '/plugin/statistics/gui', fetcher.splash)
    app.router.add_route('*', '/get/abilities', fetcher.get_abilities)
    # TODO: Add more specific routes for other statistics sources


class AbilityFetcher:

    def __init__(self, services):
        self.services = services
        self.auth_svc = services.get('auth_svc')

    async def get_abilities(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        return web.json_response(dict(abilities=[a.display for a in abilities]))

    @template('statistics.html')
    async def splash(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        technique_ids = {}
        overall = {"techniques": 0,
                   "windows": 0,
                   "linux": 0,
                   "darwin": 0,
                   "tactics": {}}
        for a in abilities:
            teid = a.display["technique_id"]
            platform = a.display["platform"]
            if teid not in technique_ids:
                technique_ids[teid] = {"total": 0,
                                       "windows": 0,
                                       "linux": 0,
                                       "darwin": 0,
                                       "technique_name": a.display["technique_name"],
                                       "tactic": a.display["tactic"]}
                overall["techniques"] += 1
                tactic = a.display["tactic"]
                if tactic not in overall["tactics"]:
                    overall["tactics"][tactic] = 0
                overall["tactics"][tactic] += 1
            overall[platform] += 1
            technique_ids[teid]["total"] += 1
            technique_ids[teid][platform] += 1

        mitre_tdds = tdds_from_url()
        missing = []
        for m in mitre_tdds:
            if m["teid"] not in technique_ids:
                missing.append(m)
        overall["missing_count"] = len(missing)
        return (dict(abilities=[a.display for a in abilities], techniques=technique_ids, overall=overall, missing=missing))