def test_which_browser(page):
    print("\n>>> BROWSER:", page.context.browser.browser_type.name)