
import logging
import os
from crmprtd import setup_logging

# log.setLevel(logging.INFO)

# # Create file handler
# log_path = os.path.join(os.path.dirname(__file__), 'fern_processing.log')
# file_handler = logging.FileHandler(log_path)
# file_handler.setLevel(logging.INFO)

# # Create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)

# # Add file handler to logger
# log.addHandler(file_handler)
setup_logging(None, '/workspaces/crmprtd/fern/fern_log.log', 'tongli1997@uvic.ca', 'DEBUG', 'fern')
log = logging.getLogger(__name__)


import sqlalchemy as sa
from sqlalchemy.orm import Session
from pycds import Variable
from crmprtd.infer import infer
import pickle
from crmprtd.more_itertools import tap, log_progress
from crmprtd.align import align
from crmprtd.insert import insert
from pprint import pprint
from crmprtd.constants import InsertStrategy

print(os.getcwd())
engine = sa.create_engine("postgresql://tongli1997@dbtest04.pcic.uvic.ca:5432/crmp", echo=False)
session = Session(engine)

# result = session.execute(sa.text("SELECT * FROM crmp.meta_network"))
# test = result.fetchall()

# print(test)

results2 = session.query(Variable).filter(Variable.network_id == 11)
test2 = results2.all()
# pprint(test2)



output_folder = '/workspaces/crmprtd/rows_output/'

# file_name = 'updated_rows_with_unit_output_Barren.pickle'
file_name = 'updated_rows_with_unit_output_Barren.pickle'
file_path = os.path.join(output_folder, file_name)

# Load the pickle file
with open(file_path, 'rb') as f:
    rows = pickle.load(f)

pprint(rows)


is_diagnostic = False
insert_strategy = InsertStrategy.BULK
bulk_chunk_size=1000
sample_size=50
network = '_test'


infer(session, rows, diagnostic = is_diagnostic)

# Filter the observations by time period, then align them.
log.info("Align + filter: start")
observations = list(
    # Note: filter(None, <collection>) removes falsy values from <collection>,
    # in this case possible None values returned by align.
    filter(
        None,
        tap(
            log_progress(
                (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000),
                "align progress: {count}",
                log.info,
            ),
            (
                align(session, row, is_diagnostic)
                for row in rows
                # if start_date <= row.time <= end_date
            ),
        ),
    )
)
log.info("Align + filter: done")

log.info(f"Count of observations to process: {len(observations)}")
if is_diagnostic:
    for obs in observations:
        log.info(obs)
else:

    log.info("Insert: start")
    results = insert(
        session,
        observations,
        strategy=insert_strategy,
        bulk_chunk_size=bulk_chunk_size,
        sample_size=sample_size,
    )
    log.info("Insert: done")
    log.info("Data insertion results", extra={"results": results, "network": network})

# Add this after setting up logging
log.info("Logging system initialized")
