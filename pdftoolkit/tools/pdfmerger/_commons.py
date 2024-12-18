from ...translation import t


def _this_t(key: str, prefix: str = "app.tools.pdfmerger", **kwargs):
    return t(key, prefix=prefix, **kwargs)
