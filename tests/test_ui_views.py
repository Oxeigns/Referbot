import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mybot.ui.strings import t
from mybot.ui.views import home_view


def test_i18n_fallback():
    assert t('home.title', 'es') == t('home.title', 'en')
    assert t('missing.key', 'en') == 'missing.key'


def test_home_view_tip_and_escape():
    user = {'name': '<Alice>', 'points': 5, 'refs': 1, 'today': 0, 'locale': 'en', 'verified': False}
    text, kb = home_view(user)
    assert t('home.tip', 'en') in text
    assert '&lt;Alice&gt;' in text
