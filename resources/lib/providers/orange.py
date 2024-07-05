# -*- coding: utf-8 -*-
"""Orange API client"""
from datetime import date, datetime
import json
from numbers import Number
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ..utils import random_ua

def get_channels():
    """Retrieve all the available channels and the the associated information (name, logo, zapping number, etc.)"""
    endpoint = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels'

    req = Request(endpoint, headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())

def get_channel_stream(channel_id):
    """Get stream information (MPD address, Widewine key) for the specified channel"""
    endpoint = \
        'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC'

    req = Request(endpoint.format(channel_id), headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    try:
        res = urlopen(req)
    except HTTPError as error:
        if error.code == 403:
            return False

    return json.loads(res.read())

def get_programs(days=None, period_start=None, period_end=None):
    """Returns all the programs for the specified period"""
    endpoint = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={}&mco=OFR'

    if isinstance(days, int) and days > 0:
        today = datetime.timestamp(datetime.combine(date.today(), datetime.min.time()))
        chunks_per_day = 2
        chunk_duration = 24 * 60 * 60 / chunks_per_day
        programs = []

        for chunk in range(0, days * chunks_per_day):
            period_start = (today + chunk_duration * chunk) * 1000
            period_end = period_start + (chunk_duration * 1000)
            programs.extend(get_programs(period_start=period_start, period_end=period_end))

        return programs

    if isinstance(period_start, Number) and isinstance(period_end, Number):
        period = '{},{}'.format(int(period_start), int(period_end))
    else:
        period = 'today'

    req = Request(endpoint.format(period), headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())