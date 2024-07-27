**Spotify Account Creator**
==========================

**Description**
---------------

This script creates Spotify accounts using random email addresses and solves CAPTCHAs. It uses a configuration file (`config.json`) to customize the account creation process.

**Configuration**
---------------

The script uses a `config.json` file to configure the account creation process. The file should contain the following settings:

* `domains`: A list of email domains to use for account creation.
* `custom_email_start`: The starting string for the email address.
* `use_proxy`: A boolean indicating whether to use a proxy for account creation.
* `use_custom_password`: A boolean indicating whether to use a custom password for account creation.
* `custom_password`: The custom password to use for account creation.
* `threads`: The number of threads to use for account creation.

**Usage**
-----

1. Create a `config.json` file with the desired settings.
2. Run the script using Python: `python main.py`
3. The script will create Spotify accounts using the configured settings.

**Dependencies**
------------

* `requests`
* `random`
* `re`
* `json`
* `threading`
* `console` (for logging)
* `solver` (for CAPTCHA solving)

## Join Our Community
- Join our Discord community for support, updates, and more: [Eclipsy Hub](https://discord.gg/eclipsyhub)
- Looking For Saudi-Arabian's Create Ticket If U Are From SA

**Note**
----

This script is for educational purposes only and should not be used to create spam accounts or violate Spotify's terms of service.

**License**
-------

This script is licensed under the MIT License. See `LICENSE` for details.
