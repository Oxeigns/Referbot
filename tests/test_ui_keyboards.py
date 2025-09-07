import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mybot.ui import keyboards, callbacks
from mybot.ui.style import EMOJIS


def test_home_keyboard_shape():
    kb = keyboards.home('en', is_owner=False)
    rows = kb.inline_keyboard
    assert [len(r) for r in rows] == [2, 2, 2]
    kb_owner = keyboards.home('en', is_owner=True)
    rows_owner = kb_owner.inline_keyboard
    assert [len(r) for r in rows_owner] == [2, 2, 2, 1]


def test_page_controls_first_middle_last():
    # first page
    row_first = keyboards.page_controls('en', 1, 3, 'test')[0]
    assert callbacks.parse(row_first[0].callback_data)['route'] == 'noop'
    assert callbacks.parse(row_first[2].callback_data)['route'] == 'test:page:2'
    # middle page
    row_mid = keyboards.page_controls('en', 2, 3, 'test')[0]
    assert callbacks.parse(row_mid[0].callback_data)['route'] == 'test:page:1'
    assert callbacks.parse(row_mid[2].callback_data)['route'] == 'test:page:3'
    # last page
    row_last = keyboards.page_controls('en', 3, 3, 'test')[0]
    assert callbacks.parse(row_last[0].callback_data)['route'] == 'test:page:2'
    assert callbacks.parse(row_last[2].callback_data)['route'] == 'noop'
