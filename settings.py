from os import environ


#SESSION_CONFIGS = [
#    dict(
#        name='guess_two_thirds',
#        display_name="Guess 2/3 of the Average",
#        app_sequence=['guess_two_thirds', 'payment_info'],
#        num_demo_participants=3,
#    ),
#    dict(
#        name='survey', app_sequence=['survey', 'payment_info'], num_demo_participants=1
#    ),
#]

#SESSION_CONFIGS = [
#    dict(
#        name='my_simple_survey',
#        num_demo_participants=3,
#        app_sequence=['my_simple_survey']
#    ),
#]


# SESSION_CONFIGS = [
#    dict(
#        name='prisoner',
#        num_demo_participants=2,
#        use_browser_bots=True,
#        app_sequence=['prisoner']
#    ),
# ]


# SESSION_CONFIGS = [
#    dict(
#        name='my_public_goods',
#        num_demo_participants=3,
#        use_browser_bots=True,
#        app_sequence=['my_public_goods']
#    ),
# ]

SESSION_CONFIGS = [
    dict(
        name='wst_mngm',
        num_demo_participants=18,
        use_browser_bots=False,
        app_sequence=['wst_mngm_main']
    ),
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['capac', 'store', 'balance', 'SurvCost', 'DropoutCounter']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = [
    dict(
        name='recycpoly',
        display_name='Recycpoly Experimental Room',
        participant_label_file='_rooms/Recycpoly.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '3322709502241'

INSTALLED_APPS = ['otree']
