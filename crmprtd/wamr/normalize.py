# Local
from crmprtd.normalize import csv_normalizer

normalize = csv_normalizer(
    'ENV-AQN',
    ['time', 'station_id', '_', 'variable_name', '_', '_', '_', 'unit', '_',
     '_', '_', 'val'],
    [
        ('% RH', '%'),
        ('\u00b0C', 'celsius'),
        ('mb', 'millibar'),
        ('Deg', 'degree')
    ]
)
