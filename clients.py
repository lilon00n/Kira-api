# -*- coding: utf-8 -*-
"""
clients.py
Client configuration lookup.

Originally this file was part of an undocumented private codebase.
This stub provides the interface expected by one_up.py and one_up_eticom.py:
  findClient(name) -> Client object with .ext and .logo attributes.

Add real clients to the CLIENTS dict or replace the lookup with a database
query as needed.
"""

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


class Client:
    """Holds client-specific branding configuration."""

    def __init__(self, name, logo=None, ext='png'):
        self.name = name
        # Full path to the logo file (used by one_up.py to load the image)
        self.logo = logo or os.path.join(DATA_PATH, 'default-logo.png')
        # File extension / format string recognised by Pillow / ReportLab
        self.ext = ext

    def __repr__(self):
        return f'<Client {self.name!r} logo={self.logo!r}>'


# -----------------------------------------------------------------------
# Add client entries here.  Key = lowercase client name as sent by Nala.
# logo = absolute or relative path to the image file.
# ext  = image format ('png', 'jpg', 'pdf', …)
# -----------------------------------------------------------------------
CLIENTS: dict[str, Client] = {
    'default': Client('Default', os.path.join(DATA_PATH, 'default-logo.png'), 'png'),
    # Example:
    # 'acme': Client('Acme Corp', os.path.join(DATA_PATH, 'logos', 'acme.png'), 'png'),
}


def findClient(name: str) -> Client:
    """Return the Client object for *name* (case-insensitive).

    Falls back to the 'default' client if the name is not registered.
    """
    return CLIENTS.get(name.lower().strip(), CLIENTS['default'])
