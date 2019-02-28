# Local
from crmprtd.normalize import csv_normalizer

normalize = csv_normalizer(
    'MVan',
    ['_', 'station_id', 'station_name', 'variable_name', '_', 'time', 'val',
     'unit', '_'],
    [
        ('% RH', '%'),
        ('C', 'celsius'),
        ('Deg_Wind', 'degree')
    ]
)
